# Copyright (c) 2024, Navari Limited and Contributors
# See license.txt


import frappe
from frappe.tests.utils import FrappeTestCase


class TestBiostarSettings(FrappeTestCase):
    def setUp(self):
        """Initialize Frappe test environment"""
        frappe.init(site="biostar.com", sites_path="/home/manu/frappe-bench/sites")
        frappe.connect()
        frappe.set_user("Administrator")

    def test_biostar_settings_creation(self):
        """Create a new Biostar Settings instance"""
        biostar_settings = frappe.get_doc(
            {
                "doctype": "Biostar Settings",
                "username": "administrator",
                "password": "test_password",
            }
        )

        biostar_settings.insert()
        self.assertIsNotNone(biostar_settings.name)

    def test_biostar_settings_validation(self):
        """Create a Biostar Settings with invalid data"""
        biostar_settings = frappe.get_doc(
            {
                "doctype": "Biostar Settings",
            }
        )

        with self.assertRaises(frappe.ValidationError):
            biostar_settings.insert()

    def tearDown(self):
        """Clean up after each test"""
        try:
            frappe.db.rollback()
        finally:
            frappe.destroy()
