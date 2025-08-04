import requests
import json
from http.cookies import SimpleCookie
from datetime import datetime

import frappe
from frappe import msgprint, _


class BiostarConnector:

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.cookie = None
        self.base_url = frappe.get_doc("Biostar Settings").ta_url

    def get_biostar_settings(self):
        return frappe.get_doc("Biostar Settings")

    def login(self):
        login_url = f"{self.base_url}/login"
        request_body = {
            "notification_token": "string",
            "mobile_device_type": "ANDROID",
            "mobile_os_version": "string",
            "mobile_app_version": "string",
            "user_id": self.username,
            "password": self.password,
        }

        headers = {
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                login_url, json=request_body, headers=headers, verify=False
            )
            response.raise_for_status()

            if response.status_code == 200:
                self.cookie = response.headers["Set-Cookie"]
                return
            else:
                frappe.throw(_("Login failed or cookie not found"))

        except Exception as e:
            frappe.log_error("Biostar Login Error", str(e))
            frappe.throw("Request failed")

    def get_attendance_ids(self, employees=None):
        attendance_ids = []
        employee_data = []
        if employees:

            employee_data = frappe.get_all(
                "Employee",
                filters={"name": ["in", employees], "status": "Active"},
                fields=["name", "attendance_device_id"],
            )

        else:
            employee_data = frappe.get_all(
                "Employee",
                fields=["attendance_device_id"],
                filters={"status": "Active"},
            )

        if not employee_data:
            frappe.throw(_("No employee with Attendance Device ID found."))

        attendance_ids = [
            emp.attendance_device_id
            for emp in employee_data
            if emp.attendance_device_id
        ]

        self.employee_ids = attendance_ids

        return attendance_ids

    def get_attendance_report(self, attendance_ids, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

        attendance_url = f"{self.base_url}/report.json"
        headers = {"Content-Type": "application/json"}

        if not self.cookie:
            self.cookie = self.login()

        headers["cookie"] = self.cookie

        request_body = {
            "type": "CUSTOM",
            "start_datetime": start_date,
            "end_datetime": end_date,
            "user_id_list": attendance_ids,
            "group_id_list": "1",
            "report_type": "REPORT_DAILY",
            "report_filter_type": "",
            "language": "en",
            "rebuild_time_card": True,
            "columns": [
                {"field": "datetime"},
                {"field": "userName"},
                {"field": "userId"},
                {"field": "inTime"},
                {"field": "outTime"},
            ],
        }

        try:
            response = requests.post(
                attendance_url,
                data=json.dumps(request_body),
                headers=headers,
                verify=False,
            )

            response.raise_for_status()
            if response.status_code == 200:
                records = response.json().get("records", [])

                if not records:
                    frappe.throw("No Checkin Data for the selected period")

                self.attendance_logs = [
                    log
                    for log in records
                    if log.get("inTime") != "-" or log.get("outTime") != "-"
                ]

        except Exception as e:
            frappe.log_error("Biostar Error", str(e))
            frappe.throw(_(f"Something went wrong"))

    def format_attendance_logs(self):
        if self.attendance_logs:
            self.attendance_logs = [
                {
                    "date": log["datetime"],
                    "in_time": log["inTime"],
                    "out_time": log["outTime"],
                    "employee_field_value": log["userId"],
                    "name": log["userName"],
                }
                for log in self.attendance_logs
            ]

        if self.attendance_logs:
            self.create_punch_logs()

    def create_punch_logs(self):
        """from the attendance report, create checkin/out logs to be sent to erpnext"""
        if self.attendance_logs:
            self.punch_logs = []
            datetime_format = "%Y/%m/%d %H:%M:%S"

            for log in self.attendance_logs:
                if log["in_time"] != "-":

                    datetime_str = f"{log['date']} {log['in_time']}"
                    log["datetime_in"] = datetime.strptime(
                        datetime_str, datetime_format
                    )

                    self.punch_logs.extend(
                        [
                            {
                                "employee_field_value": log["employee_field_value"],
                                "timestamp": log["datetime_in"],
                                "log_type": "IN",
                            }
                        ]
                    )

                if log["out_time"] != "-":

                    datetime_str = f"{log['date']} {log['out_time']}"
                    log["datetime_out"] = datetime.strptime(
                        datetime_str, datetime_format
                    )

                    self.punch_logs.extend(
                        [
                            {
                                "employee_field_value": log["employee_field_value"],
                                "timestamp": log["datetime_out"],
                                "log_type": "OUT",
                            }
                        ]
                    )

        if self.punch_logs:
            add_checkin_data(self.punch_logs, self.end_date)
            self.update_last_sync_employee_date()
            self.set_last_sync_of_checkin_as_now()

    def update_last_sync_employee_date(self):
        employee_ids = self.employee_ids
        end_date = self.end_date

        employees = frappe.get_all(
            "Employee",
            filters={"attendance_device_id": ["in", employee_ids]},
            fields=["name", "attendance_device_id"],
        )

        updates = {}
        for emp in employees:
            updates[emp.name] = {
                "custom_last_attendance_sync_date": end_date,
            }

        frappe.db.bulk_update("Employee", updates, update_modified=False)

    def set_last_sync_of_checkin_as_now(self):
        shift_types = frappe.db.get_all(
            "Shift Type", filters={"enable_auto_attendance": 1}, pluck="name"
        )

        for shift_type in shift_types:
            frappe.db.set_value(
                "Shift Type",
                shift_type,
                "last_sync_of_checkin",
                datetime.now(),
                update_modified=False,
            )
            frappe.db.commit()


def is_cookie_expired(cookie_string):
    """parse cookie string"""
    cookie = SimpleCookie()
    cookie.load(cookie_string)

    """extract 'expires' attribute"""
    bs_ta_session_id_cookie = cookie.get("bs-ta-session-id")

    """ Check if 'bs-ta-session-id' cookie exists and has 'expires' attribute """
    if bs_ta_session_id_cookie is None or "expires" not in bs_ta_session_id_cookie:
        return False

    expires = bs_ta_session_id_cookie["expires"]

    expires_date = datetime.strptime(expires, "%a, %d %b %Y %H:%M:%S %Z")

    return expires_date <= datetime.utcnow()


def add_checkin_data(punch_logs, end_date):
    msgprint(_("The task has been enqueued as a background job."), alert=True)
    frappe.enqueue(
        "navari_frappehr_biostar.controllers.utils.biostar_connector.create_employee_checkins",
        queue="long",
        punch_logs=punch_logs,
        end_date=end_date,
        is_async=True,
    )


def create_employee_checkins(punch_logs, end_date=None):
    device_ids = [log.get("employee_field_value") for log in punch_logs]
    employees = frappe.get_all(
        "Employee",
        filters={"attendance_device_id": ["in", device_ids]},
        fields=["name", "attendance_device_id"],
    )
    emp_map = {emp.attendance_device_id: emp.name for emp in employees}

    for punch_log in punch_logs:
        employee_name = emp_map.get(punch_log.get("employee_field_value"))
        if not employee_name:
            frappe.log_error(
                f"Employee not found for device ID: {punch_log.get('employee_field_value')}"
            )
            continue

        try:
            doc = frappe.new_doc("Employee Checkin")
            doc.update(
                {
                    "employee": employee_name,
                    "log_type": punch_log.get("log_type"),
                    "time": punch_log.get("timestamp"),
                }
            )
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.db.rollback()
            error_msg = f"Failed checkin for {punch_log.get('employee_field_value')} at {punch_log.get('timestamp')}. Error: {str(e)}"
            frappe.log_error(error_msg)
