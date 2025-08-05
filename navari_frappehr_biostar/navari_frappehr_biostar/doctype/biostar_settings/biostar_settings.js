// Copyright (c) 2024, Navari Limited and contributors
// For license information, please see license.txt
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
    frappe.call({
      method:
        "navari_frappehr_biostar.controllers.biostar_calls.get_employee_checkins",
      args: {
        start_date: frm.doc.start_date,
        end_date: frm.doc.end_date,
      },
      error: function () {
        frappe.msgprint(__("Failed to start fetch attendance data"));
      },
      freeze: true,
      freeze_message: "Gettting data...",
    });
  },
});
