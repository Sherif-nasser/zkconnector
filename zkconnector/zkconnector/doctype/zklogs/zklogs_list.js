frappe.listview_settings['ZKLogs'] = {
    onload: function(listview) {
	// listview.page.add_inner_button(__("Sync Devices"), function() {
	//     frappe.call({
	// 	method: 'zkconnector.api.sync_logs',
	// 	callback: function(r){
	// 	    console.log(r.message)
	// 	}
	//     })
	// });
	listview.page.add_inner_button(__("Sync Logs"), function() {
	    frappe.show_progress("Syncing Logs", 2, 6, "Loading")
	    frappe.call({
		method: 'zkconnector.api.sync_logs',
		callback: function(r){
		    frappe.show_progress("Syncing Logs", 6, 6, "Loading");
		    frappe.hide_progress();
		    if(r.message) {
			let response = r.message;
			if(r.message.devices.length > 0) {
			    frappe.show_alert({
				message:__(`can't connect to ${response.devices}`),
				indicator:'red'
			    }, 5);
			    frappe.show_alert({
				message:__(`Logs Loaded Successfully`),
				indicator:'green'
			    }, 2);
			} else {
			    frappe.show_alert({
				message:__(`Logs Loaded Successfully`),
				indicator:'green'
			    }, 2);
			}
		    }
		}
	    });
	});
    }
}
