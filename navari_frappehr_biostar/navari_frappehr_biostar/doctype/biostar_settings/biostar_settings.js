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

frappe.ui.form.on("Biostar Settings", {
  refresh: function (frm) {
    if (
      frm.doc.username &&
      frm.doc.password &&
      frm.doc.ta_url &&
      frm.doc.start_date &&
      frm.doc.end_date
    ) {
      frm
        .add_custom_button(__("Fetch Attendance Logs"), function () {
          if (frm.doc.start_date > frm.doc.end_date) {
            frappe.msgprint({
              title: __("Error"),
              indicator: "red",
              message: __("Start Date cannot be greater than End Date"),
            });

            return;
          }

          frm.events.fetch_attendance_logs(frm);
        })
        .addClass("btn-primary");
    }
  },

  fetch_attendance_logs: function (frm) {
    loader.style.display = "block";
    frappe.call({
      method:
        "navari_frappehr_biostar.controllers.biostar_calls.get_employee_checkins",
      args: {
        start_date: frm.doc.start_date,
        end_date: frm.doc.end_date,
      },
    });
  },
});
