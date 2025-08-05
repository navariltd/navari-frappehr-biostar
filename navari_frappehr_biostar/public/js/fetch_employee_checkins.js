// Copyright (c) 2024, Navari Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
  refresh: function (frm) {
    frm
      .add_custom_button(__("Fetch Attendance"), function () {
        let d = new frappe.ui.Dialog({
          title: "Fetch Attendance",
          fields: [
            {
              label: "Start Date",
              fieldname: "start_date",
              fieldtype: "Date",
              default: frm.doc.custom_last_attendance_sync_date,
              reqd: 1,
            },
            {
              label: "End Date",
              fieldname: "end_date",
              fieldtype: "Date",
              reqd: 1,
            },
          ],
          primary_action_label: "Fetch",
          primary_action: function (data) {
            d.hide();
            const start_date = data.start_date;
            const end_date = data.end_date;

            if (start_date > end_date) {
              frappe.msgprint({
                title: __("Error"),
                indicator: "red",
                message: __("Start Date cannot be greater than End Date"),
              });

              return;
            }

            frappe.call({
              method:
                "navari_frappehr_biostar.controllers.biostar_calls.get_employee_checkins",
              args: {
                start_date: start_date,
                end_date: end_date,
                employees: [{ name: frm.doc.name }],
              },
              error: function () {
                frappe.msgprint(__("Failed to start fetch attendance data"));
              },
              freeze: true,
              freeze_message: "Gettting data...",
            });
          },
        });
        d.show();
      })
      .addClass("btn-primary");
  },
});
