# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.addons.base.tests.common import BaseCommon


class TestProjectTaskTimesheets(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "timesheet_portal_visibility": "default",
            }
        )

        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )

        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "partner_id": cls.partner.id,
            }
        )

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": cls.env.user.id,
                "company_id": cls.env.company.id,
            }
        )

    def _create_timesheet(self, invoiced=False):
        vals = {
            "name": "TS",
            "task_id": self.task.id,
            "employee_id": self.employee.id,
            "partner_id": self.partner.id,
            "unit_amount": 2,
        }
        if invoiced:
            invoice = self.env["account.move"].create(
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner.id,
                }
            )
            vals["timesheet_invoice_id"] = invoice.id
        else:
            vals["timesheet_invoice_id"] = False

        self.env["account.analytic.line"].create(vals)
        self.task.invalidate_recordset(["show_amount_due"])

    def test_amount_due_all_mode(self):
        self.partner.timesheet_portal_visibility = "all"
        self._create_timesheet(invoiced=False)
        self.assertTrue(self.task.show_amount_due)

    def test_amount_due_invoiced_mode_blocked(self):
        self.partner.timesheet_portal_visibility = "invoiced"
        self._create_timesheet(invoiced=False)
        self.assertFalse(self.task.show_amount_due)

    def test_amount_due_invoiced_mode_allowed(self):
        self.partner.timesheet_portal_visibility = "invoiced"
        self._create_timesheet(invoiced=True)
        self.assertTrue(self.task.show_amount_due)
