# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import date, timedelta

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetDayWeek(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.timesheet_line_model = cls.env["account.analytic.line"]
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan", "default_applicability": "optional"}
        )
        cls.analytic = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "plan_id": cls.analytic_plan.id,
                "company_id": False,
            }
        )
        cls.user = cls.env.ref("base.user_root")
        # 2024-10-14 was a Monday = day "0" of a week
        cls.base_date = date(2024, 10, 14)
        cls.base_line = {
            "name": "test",
            "date": cls.base_date,
            "user_id": cls.user.id,
            "unit_amount": 2.0,
            "account_id": cls.analytic.id,
            "amount": -60.0,
        }

    def test_01_week_day(self):
        timesheet = self.timesheet_line_model.create(self.base_line)
        for i in range(0, 7):
            timesheet.date = self.base_date + timedelta(days=i)
            self.assertEqual(timesheet.day_week, str(i))

    def test_02_week_day_report(self):
        timesheet_rpt = self.env["timesheets.analysis.report"].browse([])
        self.assertTrue(timesheet_rpt._select(), "A.day_week AS day_week")
