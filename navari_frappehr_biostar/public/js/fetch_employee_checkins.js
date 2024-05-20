

// Copyright (c) 2024, Navari Limited and contributors
// For license information, please see license.txt
let loader = document.createElement("div");
loader.className = "loader";
loader.style.display = "none";

document.body.appendChild(loader);

let css =
  ".loader { border: 8px solid #f3f3f3; border-top: 8px solid #3498db; border-radius: 50%; width: 40px; height: 40px; margin-left: 50%; position: fixed; bottom: 50% ; animation: spin 2s linear infinite; } @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }";

let style = document.createElement("style");
style.appendChild(document.createTextNode(css));
document.head.appendChild(style);

frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.add_custom_button(__('Fetch Attendance'), function() {
            let d = new frappe.ui.Dialog({
                title: 'Fetch Attendance',
                fields: [
                    {
                        label: 'Start Date',
                        fieldname: 'start_date',
                        fieldtype: 'Date',
                        default:frm.doc.custom_last_attendance_sync_date,
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
                    loader.style.display = "block";
                    frappe.call({
                        method: 'navari_frappehr_biostar.controllers.biostar_calls.fetch_single_employee_attendance',
                        args: {
                            start_date: data.start_date,
                            end_date: data.end_date,
                            employee: frm.doc.name
                        },
                        callback: function(r) {
                            loader.style.display = "none";
                            if (r.message) {
                                frappe.msgprint(r.message);
                            }
                        }
                    });
                }
            });
            d.show();
        }).addClass("btn-primary");;
    }
});

