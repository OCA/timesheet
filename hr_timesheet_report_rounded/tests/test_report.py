from odoo import fields
from odoo.tests.common import TransactionCase


class TestHrTimesheetReportEntry(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create a project allowing timesheets
        self.project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "allow_timesheets": True,
            }
        )
        # Ensure no rounding by default
        self.project.write({"timesheet_rounding_method": "NO"})
        # Create an employee for timesheet lines
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": self.env.uid,
                "company_id": self.env.company.id,
            }
        )
        # Hour UoM
        self.uom = self.env.ref("uom.product_uom_hour")
        # Get existing report group (loaded by hr_timesheet_report)
        self.report_group = self.env["hr.timesheet.report.group"].search([], limit=1)
        if not self.report_group:
            self.skipTest("hr_timesheet_report.group data not loaded")
        # Models
        self.AAL = self.env["account.analytic.line"]
        self.ReportEntry = self.env["hr.timesheet.report.entry"]

    def _make_lines(self, amounts):
        """Helper to create analytic lines with given unit_amounts."""
        lines = []
        for amt in amounts:
            vals = {
                "project_id": self.project.id,
                "account_id": self.project.analytic_account_id.id,
                "employee_id": self.employee.id,
                "unit_amount": amt,
                "product_uom_id": self.uom.id,
                "date": fields.Date.today(),
                "name": "Test",
            }
            lines.append(self.AAL.create(vals))
        return lines

    def test_no_rounding(self):
        """Without rounding, total == sum(unit_amount)."""
        lines = self._make_lines([1.5, 2.5])
        entry = self.ReportEntry.create(
            {
                "scope": "[]",
                "group_id": self.report_group.id,
            }
        )
        entry._compute_total_unit_amount()
        expected = sum(line.unit_amount for line in lines)
        self.assertAlmostEqual(entry.total_unit_amount, expected)

    def test_half_up_rounding(self):
        """With HALF_UP rounding to nearest whole, total == sum(unit_amount_rounded)."""
        # Set rounding to nearest 1 unit, HALF_UP
        self.project.write(
            {
                "timesheet_rounding_unit": 1.0,
                "timesheet_rounding_method": "HALF_UP",
                "timesheet_rounding_factor": 100,
            }
        )
        self._make_lines([1.2, 1.6])
        entry = self.ReportEntry.create(
            {
                "scope": "[]",
                "group_id": self.report_group.id,
            }
        )
        entry._compute_total_unit_amount()
        # 1.2 -> 1, 1.6 -> 2 => total 3
        self.assertAlmostEqual(entry.total_unit_amount, 3.0)

    def test_default_scope(self):
        """When scope is falsy, TRUE_DOMAIN branch sums all lines."""
        self._make_lines([2.0, 3.0])
        entry = self.ReportEntry.create(
            {
                "group_id": self.report_group.id,
            }
        )
        entry._compute_total_unit_amount()
        self.assertAlmostEqual(entry.total_unit_amount, 5.0)

    def test_scope_filter(self):
        """When scope is provided, safe_eval branch filters lines correctly."""
        # Create two lines, only one matches the filter
        l1, l2 = self._make_lines([1.0, 2.0])
        domain = "[('id', 'in', [%d])]" % l2.id
        entry = self.ReportEntry.create(
            {
                "scope": domain,
                "group_id": self.report_group.id,
            }
        )
        entry._compute_total_unit_amount()
        # Only l2 should be counted
        self.assertAlmostEqual(entry.total_unit_amount, l2.unit_amount)
