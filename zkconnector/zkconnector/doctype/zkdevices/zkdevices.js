// Copyright (c) 2022, Ahmed and contributors
// For license information, please see license.txt

frappe.ui.form.on('ZKDevices', {
    refresh: function(frm) {
	if(!frm.doc.__unsaved) {
	    frm.add_custom_button("Sync Device Logs", () => {
		frappe.call({
		    method: 'zkconnector.api.sync_logs',
		    args: {
			'device_name': frm.doc.device_name
		    },
		    callback: function(r){
			if(r.message) {
			    let response = r.message;
			    if(r.message.devices.length > 0) {
				frappe.show_alert({
				    message:__(`can't connect to ${response.devices}`),
				    indicator:'red'
				}, 5);
			    } else {
				frappe.show_alert({
				    message:__(`Logs Synced Successfully`),
				    indicator:'green'
				}, 2);
			    }
			}
		    }
		});
	    });

	    frm.add_custom_button("Remove Logs From Device", () => {
		frappe.call({
		    method: 'zkconnector.api.remove_logs_from_device',
		    args: {
			'device_name': frm.doc.device_name
		    },
		    callback: function(r) {
			if(r.message)
			    frappe.show_alert({
				message:__(`Logs deleted successfully`),
				indicator:'green'
			    }, 2);
		    }
		})
	    });
	}
    },
});
