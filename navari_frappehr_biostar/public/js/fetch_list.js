frappe.listview_settings['Employee'].onload = function(listview) {
    listview.page.add_action_item(__("Fetch Attendance"), function() {
        submit_employee_list(listview, "Employee");
    });
};

function submit_employee_list(listview, doctype) {
    let names = [];
    $.each(listview.get_checked_items(), function(key, value) {
        names.push(value.name);
    });

    if (names.length === 0) {
        frappe.throw(__("No rows selected."));
    }

    let d = new frappe.ui.Dialog({
        title: 'Fetch Attendance',
        fields: [
            {
                label: 'Start Date',
                fieldname: 'start_date',
                fieldtype: 'Date',
                default: frappe.datetime.nowdate(),  
                reqd: 1
            },
            {
                label: 'End Date',
                fieldname: 'end_date',
                fieldtype: 'Date',
                reqd: 1
            }
        ],
        primary_action_label: 'Fetch',
        primary_action: function(data) {
            d.hide();
            let loader = document.getElementById('loader'); 
            if (loader) {
                loader.style.display = "block";
            }
            frappe.call({
                method: 'navari_frappehr_biostar.controllers.biostar_calls.fetch_attendance_logs_for_list_employees',
                args: {
                    start_date: data.start_date,
                    end_date: data.end_date,
                    employees: names
                },
                callback: function(r) {
                    if (loader) {
                        loader.style.display = "none";
                    }
                    if (r.message) {
                        frappe.msgprint(r.message);
                    }
                }
            });
        }
    });
    d.show();
}
