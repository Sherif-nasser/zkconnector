import frappe
from dateutil import parser
import json
import sys, os
import datetime
from frappe import publish_progress

frappe.utils.sys.path.insert(1,frappe.utils.get_bench_path()+"/apps/zkconnector/zkconnector/pyzk")
from zk import ZK, const


@frappe.whitelist()
def sync_logs(device_name = None):
    if device_name:
        devices = frappe.get_all('ZKDevices',
                                 filters={'device_name':device_name})
    else:
        devices = frappe.get_all("ZKDevices", filters={'active': 1})

    disconnect_devices = []
    # count = 0
    # publish_progress(percent=10, title="Syncing logs")
    for d in devices:
        device = frappe.get_doc('ZKDevices', d)
        zk = ZK(device.ip, int(device.port), timeout=30, password=device.password, force_udp=True, ommit_ping = False)

        try:
            zk.connect()
            if device.status == "Disconnected":
                device.status = "Connected"
                device.save()
            # count += 1
        except:
            device.status = "Disconnected"
            device.save()
            frappe.db.commit()
            disconnect_devices.append(device.name)
            continue

        try:
            last = frappe.get_list('ZKLogs', filters={'device_name':device.name},\
                               order_by='date desc, time desc', limit=1)[0]
            
            last_saved_log = frappe.get_doc('ZKLogs', last) #last log in frappe
            last_saved_log_date =  parser.parse(str(last_saved_log.date))
            last_saved_log_time = parser.parse(str(last_saved_log.time))
        except:
            last_saved_log = datetime.datetime.now()
            last_saved_log_date =  parser.parse(str(last_saved_log.date()))
            last_saved_log_time = parser.parse(str(last_saved_log.time()))
        
        logs = zk.get_attendance()
        # percent = int((count/len(devices)) * 100)
        # publish_progress(percent=percent, title="Syncing logs")
        
        if len(logs) > 0: last_log = logs[-1] # last log on the device
        else: continue

        try:
            last_log_date, last_log_time = last_log.timestamp.isoformat().split("T")
        except:
            last_log_date, last_log_time = last_log.timestamp.split()

        if parser.parse(str(last_log_date)) != last_saved_log_date or \
           parser.parse(str(last_log_time)) !=  last_saved_log_time:
                
            for log in logs[::-1]:
                try:
                    log_d, log_t = log.timestamp.isoformat().split("T")
                except:
                    log_d, log_t = log.timestamp.split()
                
                if parser.parse(str(log_d)) == last_saved_log_date and\
                   parser.parse(str(log_t)) ==  last_saved_log_time:
                    break
                try:
                    l = frappe.new_doc("ZKLogs")
                    l.user_id = log.user_id
                    l.date = log_d
                    l.time = log_t
                    l.status = log.status
                    l.device_name = device.name
                    if log.punch == 0: l.log_type = "IN"
                    else: l.log_type = "OUT"
                    l.save()
                    if frappe.db.exists('Employee', {'attendance_device_id': log.user_id}):
                        employee = frappe.get_doc('Employee', {'attendance_device_id': log.user_id})
                        if not frappe.db.exists('Employee Checkin', {'employee': employee.name, 'time': f'{log_d} {log_t}'}):
                            check = frappe.new_doc("Employee Checkin")
                            check.employee = employee.name
                            check.time = f'{log_d} {log_t}'
                            if log.punch == 0: check.log_type = "IN"
                            else: check.log_type = "OUT"
                            check.save()
                except:
                    pass
    
    frappe.db.commit()
    # publish_progress(percent=100, title="Syncing logs")
    return {'devices': disconnect_devices}

@frappe.whitelist()
def connect_devices():
    devices = frappe.get_all("ZKDevices", filters={'active': 1})
    failed_devices = []
    count = 0
    
    for d in devices:
        device =  frappe.get_doc('ZKDevices', d)
        zk = ZK(device.ip, int(device.port), timeout=5, password=device.password, force_udp=True, ommit_ping = False)
        try:
            zk.connect()
            if device.status != "Connected":
                device.status = "Connected"
                device.save()
        except:
            device.status = "Disconnected"
            device.save()
            failed_devices.append(device.name)
        count += 1
        percent = int(count/len(devices) * 100)
        publish_progress(percent=percent, title="Connecting")

    frappe.db.commit()
    return {'failed_devices': failed_devices}

@frappe.whitelist()
def disconnect_devices():
    devices = frappe.get_all("ZKDevices")
    for d in devices:
        device =  frappe.get_doc('ZKDevices', d)
        device.status = "Disconnected"
        device.save()
    frappe.db.commit()



@frappe.whitelist()
def remove_logs_from_device(device_name):
    try:
        device = frappe.get_doc("ZKDevices", device_name)
        zk = ZK(device.ip, int(device.port), timeout=5, password=device.password, force_udp=True, ommit_ping = False)
        zk.connect()
        zk.clear_attendance()
    except:
        frappe.throw(f"Can't Connect to {device_name}")
