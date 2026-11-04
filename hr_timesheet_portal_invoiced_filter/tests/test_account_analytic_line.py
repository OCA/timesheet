# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestTimesheetPortalDomain(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "company_id": cls.company.id,
            }
        )
        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal Test",
                "login": f"portal_test_{cls.env.uid}",
                "group_ids": [(6, 0, [cls.env.ref("base.group_portal").id])],
                "partner_id": cls.partner.id,
            }
        )
        cls.portal_env = cls.env(user=cls.portal_user.id)

    def _set_user_partner(self, partner):
        self.portal_user.write({"partner_id": partner.id if partner else False})

    def test_domain_default_mode(self):
        self._set_user_partner(self.partner)
        self.partner.timesheet_portal_visibility = "all"
        domain = self.portal_env["account.analytic.line"]._timesheet_get_portal_domain()
        self.assertNotIn(("timesheet_invoice_id", "!=", False), domain)

    def test_domain_invoiced_mode(self):
        self._set_user_partner(self.partner)
        self.partner.timesheet_portal_visibility = "invoiced"
        employee = self.env["hr.employee"].sudo().search([], limit=1)
        self.env["account.analytic.line"].sudo().create(
            {
                "name": "TS",
                "unit_amount": 2,
                "employee_id": employee.id,
                "partner_id": self.partner.id,
                "timesheet_invoice_id": False,
            }
        )
        domain = self.portal_env["account.analytic.line"]._timesheet_get_portal_domain()
        self.assertTrue(any(d == ("timesheet_invoice_id", "!=", False) for d in domain))

    def test_domain_no_partner_safe(self):
        self._set_user_partner(None)
        domain = self.portal_env["account.analytic.line"]._timesheet_get_portal_domain()
        self.assertNotIn(("timesheet_invoice_id", "!=", False), domain)

    def test_commercial_partner_invoiced_applies_filter(self):
        parent = self.env["res.partner"].create(
            {
                "name": "Parent",
                "company_id": self.company.id,
                "timesheet_portal_visibility": "invoiced",
            }
        )
        child = self.env["res.partner"].create(
            {
                "name": "Child",
                "company_id": self.company.id,
                "parent_id": parent.id,
            }
        )
        self.portal_user.write({"partner_id": child.id})
        domain = self.portal_env["account.analytic.line"]._timesheet_get_portal_domain()
        self.assertTrue(any(d == ("timesheet_invoice_id", "!=", False) for d in domain))

    def test_hr_timesheet_user_returns_base_domain(self):
        user = self.env["res.users"].create(
            {
                "name": "Timesheet User",
                "login": "ts_user",
                "group_ids": [
                    (6, 0, [self.env.ref("hr_timesheet.group_hr_timesheet_user").id])
                ],
                "partner_id": self.partner.id,
            }
        )
        env = self.env(user=user.id)
        domain = env["account.analytic.line"]._timesheet_get_portal_domain()
        self.assertNotIn(("timesheet_invoice_id", "!=", False), domain)
