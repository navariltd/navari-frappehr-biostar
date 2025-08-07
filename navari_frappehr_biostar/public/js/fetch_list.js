frappe.listview_settings["Employee"].onload = function (listview) {
  listview.page.add_action_item(__("Fetch Attendance"), function () {
    submit_employee_list(listview, "Employee");
  });
};

function submit_employee_list(listview, doctype) {
  let employees = [];
  $.each(listview.get_checked_items(), function (key, value) {
    employees.push({ name: value.name });
  });

  if (employees.length === 0) {
    frappe.throw(__("No rows selected."));
  }

  let d = new frappe.ui.Dialog({
    title: "Fetch Attendance",
    fields: [
      {
        label: "Start Date",
        fieldname: "start_date",
        fieldtype: "Date",
        default: frappe.datetime.nowdate(),
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
          employees: employees,
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
}
