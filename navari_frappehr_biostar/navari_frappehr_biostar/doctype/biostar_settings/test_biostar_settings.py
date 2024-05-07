# Copyright (c) 2024, Navari Limited and Contributors
# See license.txt


import frappe
from frappe.tests.utils import FrappeTestCase


class TestBiostarSettings(FrappeTestCase):
    def setUp(self):
        """Initialize Frappe test environment"""
        frappe.init(site="", sites_path="")

    def test_biostar_settings_creation(self):
        """Create a new Biostar Settings instance"""
        biostar_settings = frappe.get_doc(
            {
                "doctype": "Biostar Settings",
                "username": "test_user",
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
        # Clean up after each test
        frappe.db.rollback()
        frappe.destroy()