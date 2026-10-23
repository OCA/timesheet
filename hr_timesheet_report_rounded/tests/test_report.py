from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetReportEntry(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "allow_timesheets": True,
                "timesheet_rounding_method": "NO",
            }
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})
        cls.uom = cls.env.ref("uom.product_uom_hour")
        cls.AAL = cls.env["account.analytic.line"]

    def _make_lines(self, amounts):
        """Create timesheet lines with the given quantities."""
        lines = self.AAL.browse()
        for amt in amounts:
            lines |= self.AAL.create(
                {
                    "project_id": self.project.id,
                    "employee_id": self.employee.id,
                    "unit_amount": amt,
                    "product_uom_id": self.uom.id,
                    "date": fields.Date.today(),
                    "name": "Test",
                }
            )
        return lines

    def _report_total(self, lines):
        """Total of a report limited to these lines.

        The report builds its own groups. A group created next to the
        report is removed when that compute runs.
        """
        report = self.env["hr.timesheet.report"].create(
            {
                "time_format": "decimal",
                "line_ids": [(6, 0, lines.ids)],
            }
        )
        return report.total_unit_amount

    def test_no_rounding(self):
        """Without rounding, the report total equals the sum of the quantities."""
        lines = self._make_lines([1.5, 2.5])
        for line in lines:
            self.assertAlmostEqual(line.unit_amount_rounded, line.unit_amount)
        self.assertAlmostEqual(
            self._report_total(lines), sum(lines.mapped("unit_amount"))
        )

    def test_half_up_rounding(self):
        """Closest rounding to 1 hour is what the report totals."""
        self.project.write(
            {
                "timesheet_rounding_unit": 1.0,
                "timesheet_rounding_method": "HALF-UP",
                "timesheet_rounding_factor": 100,
            }
        )
        lines = self._make_lines([1.2, 1.6])
        self.assertAlmostEqual(lines[0].unit_amount_rounded, 1.0)
        self.assertAlmostEqual(lines[1].unit_amount_rounded, 2.0)
        self.assertAlmostEqual(self._report_total(lines), 3.0)

    def test_scope_filter(self):
        """A report on one line totals only that line."""
        lines = self._make_lines([1.0, 2.0])
        self.assertAlmostEqual(
            self._report_total(lines[1]), lines[1].unit_amount_rounded
        )
