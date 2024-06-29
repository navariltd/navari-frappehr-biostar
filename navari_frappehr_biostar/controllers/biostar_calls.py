import json
import requests
import frappe
from frappe.utils import today, get_url
from frappe.utils.password import get_decrypted_password
from http.cookies import SimpleCookie

import ast
from datetime import datetime

SETTINGS_DOCTYPE = "Biostar Settings"
username = frappe.db.get_single_value(SETTINGS_DOCTYPE, "username")
password = get_decrypted_password(SETTINGS_DOCTYPE, SETTINGS_DOCTYPE, "password")
erpnext_instance_url = get_url().__str__()
ta_base_url = frappe.db.get_single_value(SETTINGS_DOCTYPE, "ta_url").__str__()


class BiostarConnect:
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.cookie = self.login()

	def login(self):
		login_url = f"{ta_base_url}/login"
		request_body = {
			"notification_token": "string",
			"mobile_device_type": "string",
			"mobile_os_version": "string",
			"mobile_app_version": "string",
			"user_id": self.username,
			"password": self.password,
		}

		try:
			response = requests.post(login_url, data=request_body, verify=False)
			if response.status_code == 200:
				return response.headers["Set-Cookie"]
			else:
				frappe.throw(
					f"Login request failed with status code: {response.status_code}"
				)
		except Exception as e:
			frappe.throw(f"An error occurred: {e}")

	def get_attendance_report(
		self, attendance_id, start_date=today().__str__(), end_date=today().__str__()):
		headers = {"Content-Type": "application/json"}
		attendance_url = f"{ta_base_url}/report.json"

		self.attendance_logs = []

		offset = 0
		limit = 200

	  
		while True:
			if not self.cookie or is_cookie_expired(self.cookie):
				self.cookie = self.login()
			headers["Cookie"] = self.cookie

			request_body = {
				"limit": limit,
				"offset": offset,
				"type": "CUSTOM",
				"start_datetime": start_date,
				"end_datetime": end_date,
				"user_id_list": [f"{attendance_id}"],
				"group_id_list": "1",
				"report_type": "REPORT_DAILY",
				"report_filter_type": "",
				"language": "en",
				"rebuild_time_card": True,
				"columns": [{}],
			}

			try:
				response = requests.post(
					attendance_url,
					data=json.dumps(request_body),
					headers=headers,
					verify=False,
				)

				if response.status_code == 200:
				
					"""no more records, break loop"""
					if not response.json()["records"]:
						if self.attendance_logs:
							"""filter for entries with only checkin/out time"""
							self.attendance_logs = [
								log
								for log in self.attendance_logs
								if log.get("inTime") != "-" or log.get("outTime") != "-"
							]
						break

					self.attendance_logs.extend(response.json()["records"])
					offset += limit
				else:
					frappe.throw(
						f"Fetching attendance logs failed with error log: {response.status_code}"
					)
					break
			except Exception as e:
				frappe.throw(f"An error occurred: {e}")
				break

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

	def create_punch_logs(self):
		"""from the attendance report, create checkin/out logs to be sent to erpnext"""
		if self.attendance_logs:
			self.punch_logs = []
			datetime_format = "%d/%m/%Y %H:%M:%S"

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


@frappe.whitelist()
def send_to_erpnext(employee_field_value, timestamp, log_type):
	employee_=frappe.get_doc("Employee", {"attendance_device_id": employee_field_value})
	try:
		new_employee_checkin=frappe.new_doc("Employee Checkin")
		new_employee_checkin.employee=employee_.name
		new_employee_checkin.log_type=log_type
		new_employee_checkin.time=timestamp
		new_employee_checkin.save()
	except Exception as e:
		frappe.log(f"An error occurred: {e}")

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


@frappe.whitelist()
def add_checkin_logs_for_current_day():
	enqueue_fetching_logs(today().__str__(), today().__str__())
	
def check_relieving_date(employee):
	if employee.relieving_date:
		relieving_date = employee.relieving_date

		first_day_of_month = frappe.utils.formatdate(frappe.utils.get_first_day(frappe.utils.today()), 'dd-MM-YYYY')

		# Format the relieving_date to 'dd-MM-YYYY'
		relieving_date_formatted = frappe.utils.formatdate(relieving_date, 'dd-MM-YYYY')
		if first_day_of_month >= relieving_date_formatted:
			return True
	return False

	
def add_checkin_logs(start_date=None, end_date=None):
	employees = frappe.db.get_all("Employee", filters={"attendance_device_id": ["!=", None], "relieving_date": ["<=", frappe.utils.get_first_day(frappe.utils.today())]},
									fields=["name", "attendance_device_id"])
	for employee in employees:
		if check_relieving_date(employee):
			continue
		
		attendance_id=employee.attendance_device_id
		biostar = BiostarConnect(username=username, password=password)
		biostar.get_attendance_report(attendance_id, start_date, end_date)
		biostar.format_attendance_logs()
		biostar.create_punch_logs()
		

		if hasattr(biostar, 'punch_logs') and biostar.punch_logs:
			for log in biostar.punch_logs:
				send_to_erpnext(
					log.get("employee_field_value"),
					log.get("timestamp"),
					log.get("log_type"),
				)
		else:
			frappe.log(f"No punch logs generated for employee: {employee.name}")

		set_last_sync_of_checkin_as_now()
		update_last_sync_employee_date(employee.name, end_date)

@frappe.whitelist()
def add_checkin_logs_for_specified_dates(start_date, end_date):   
	enqueue_fetching_logs(start_date, end_date)
		
#Push the job to the queue, background job
def enqueue_fetching_logs(start_date, end_date):
	job_id = frappe.enqueue(
		"navari_frappehr_biostar.controllers.biostar_calls.add_checkin_logs_for_specified_date",           
		queue="long",
		start_date=start_date,
		end_date=end_date,
		timeout=2700,
		is_async=True,
		at_front=False,
	)
	return job_id

@frappe.whitelist()
def add_checkin_logs_for_specified_date(start_date, end_date):
	add_checkin_logs(start_date=start_date, end_date=end_date)
   

def set_last_sync_of_checkin_as_now():
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

@frappe.whitelist()
def fetch_single_employee_attendance(start_date, end_date, employee):
	employee_doc = frappe.get_doc('Employee', employee)
	if not employee_doc.attendance_device_id:
		frappe.throw(f'Employee {employee_doc.name} does not have an attendance device ID.')

	biostar = BiostarConnect(username=username, password=password)
	biostar.get_attendance_report(employee_doc.attendance_device_id, start_date, end_date)
	biostar.format_attendance_logs()
	biostar.create_punch_logs()
	update_last_sync_employee_date(employee, end_date)

	if hasattr(biostar, 'punch_logs') and biostar.punch_logs:
		for log in biostar.punch_logs:
			send_to_erpnext(
				log.get('employee_field_value'),
				log.get('timestamp'),
				log.get('log_type')
			)
		return f'Attendance logs for {employee_doc.name} from {start_date} to {end_date} fetched successfully.'
	else:
		return f'No attendance logs found for {employee_doc.name} from {start_date} to {end_date}.'


def update_last_sync_employee_date(employee, end_date):
	employee=frappe.get_doc('Employee', employee)
	employee.custom_last_attendance_sync_date=end_date
	employee.save()
	
def fetch_attendance_list(start_date, end_date, employees):
	
	for employee in employees:
		employee_doc = frappe.get_doc('Employee', employee)
		attendance_id=employee_doc.attendance_device_id
		biostar = BiostarConnect(username=username, password=password)
		biostar.get_attendance_report(attendance_id, start_date, end_date)
		biostar.format_attendance_logs()
		biostar.create_punch_logs()
		

		if hasattr(biostar, 'punch_logs') and biostar.punch_logs:
			for log in biostar.punch_logs:
				send_to_erpnext(
					log.get("employee_field_value"),
					log.get("timestamp"),
					log.get("log_type"),
				)
		else:
			frappe.log(f"No punch logs generated for employee: {employee_doc.name}")

		set_last_sync_of_checkin_as_now()
		update_last_sync_employee_date(employee_doc.name, end_date)
  
@frappe.whitelist()
def fetch_attendance_logs_for_list_employees(start_date, end_date, employees):
	employee_list = ast.literal_eval(employees)#converts the string to a list
	enqueue_fetching_logs_list(start_date, end_date, employee_list)

def enqueue_fetching_logs_list(start_date, end_date, employees):
	job_id = frappe.enqueue(
		"navari_frappehr_biostar.controllers.biostar_calls.fetch_attendance_list",           
		queue="long",
		start_date=start_date,
		end_date=end_date,
		employees=employees,
		timeout=2700,
		is_async=True,
		at_front=False,
	)
	return job_id
