import frappe
from .utils.biostar_connector import BiostarConnector
from frappe.utils.password import get_decrypted_password

SETTINGS_DOCTYPE = "Biostar Settings"


def get_biostar_settings():
    return frappe.get_doc(SETTINGS_DOCTYPE)


@frappe.whitelist()
def get_employee_checkins(start_date, end_date, employees=None):
    attendance_ids = []
    settings = get_biostar_settings()
    if not settings.active:
        frappe.throw("Biostar is Inactive")

    password = get_decrypted_password(SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, "password")
    username = settings.username

    biostar = BiostarConnector(username, password)

    biostar.login()
    if employees:
        if isinstance(employees, str):
            employees = frappe.parse_json(employees)
        employees = [emp.get("name") for emp in employees]
        attendance_ids = biostar.get_attendance_ids(employees)
    else:
        attendance_ids = biostar.get_attendance_ids()

    biostar.get_attendance_report(attendance_ids, start_date, end_date)
    biostar.format_attendance_logs()
