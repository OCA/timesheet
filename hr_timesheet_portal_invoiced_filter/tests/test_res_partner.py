# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestResPartner(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write({"timesheet_portal_visibility": "invoiced"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

    def test_direct_value(self):
        self.partner.timesheet_portal_visibility = "all"
        self.assertEqual(
            self.partner._get_timesheet_portal_visibility(),
            "all",
        )

    def test_default_fallback(self):
        self.partner.timesheet_portal_visibility = "default"

        self.assertEqual(
            self.partner._get_timesheet_portal_visibility(),
            "invoiced",
        )

    def test_invoiced(self):
        self.partner.timesheet_portal_visibility = "invoiced"
        self.assertEqual(
            self.partner._get_timesheet_portal_visibility(),
            "invoiced",
        )
