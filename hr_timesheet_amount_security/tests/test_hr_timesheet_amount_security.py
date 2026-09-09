# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrTimesheetAmountSecurity(TransactionCase):
    """Test cases for hr_timesheet_amount_security module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_amount_group = cls.env.ref(
            "analytic_amount_security.group_allow_read_analytic_amount"
        )

    def test_amount_field_has_groups(self):
        """Test that amount field has the correct groups restriction."""
        amount_field = self.env["timesheets.analysis.report"]._fields["amount"]
        self.assertTrue(amount_field.groups)
        self.assertEqual(
            amount_field.groups,
            "analytic_amount_security.group_allow_read_analytic_amount",
        )

    def test_cost_fields_have_groups(self):
        """Test that cost fields have the correct groups restriction."""
        timesheets_cost_field = self.env["hr.timesheet.attendance.report"]._fields[
            "timesheets_cost"
        ]
        self.assertTrue(timesheets_cost_field.groups)
        self.assertEqual(
            timesheets_cost_field.groups,
            "analytic_amount_security.group_allow_read_analytic_amount",
        )

        attendance_cost_field = self.env["hr.timesheet.attendance.report"]._fields[
            "attendance_cost"
        ]
        self.assertTrue(attendance_cost_field.groups)
        self.assertEqual(
            attendance_cost_field.groups,
            "analytic_amount_security.group_allow_read_analytic_amount",
        )

        cost_difference_field = self.env["hr.timesheet.attendance.report"]._fields[
            "cost_difference"
        ]
        self.assertTrue(cost_difference_field.groups)
        self.assertEqual(
            cost_difference_field.groups,
            "analytic_amount_security.group_allow_read_analytic_amount",
        )
