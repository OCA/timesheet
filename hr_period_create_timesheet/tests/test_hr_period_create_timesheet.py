# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import calendar
import time
from datetime import datetime

from odoo.tests import common
from odoo.tools.safe_eval import safe_eval


class TestHRPeriodCreateTimesheet(common.TransactionCase):
    def setUp(self):
        super(TestHRPeriodCreateTimesheet, self).setUp()
        self.user_model = self.env["res.users"]
        self.company_model = self.env["res.company"]
        self.payslip_model = self.env["hr.payslip"]
        self.run_model = self.env["hr.payslip.run"]
        self.fy_model = self.env["hr.fiscalyear"]
        self.period_model = self.env["hr.period"]
        self.data_range_type_model = self.env["date.range.type"]
        self.timesheet_sheet = self.env["hr_timesheet.sheet"]
        self.hr_employee = self.env["hr.employee"]
        self.create_timesheet = self.env["hr.period.create.timesheet"]
        self.project_2 = self.env.ref("project.project_project_2")
        self.root = self.env.ref("hr.employee_admin")
        self.dept = self.env.ref("hr.employee_vad")
        self.dept_1 = self.env.ref("hr.dep_rd")
        self.dept.write({"parent_id": self.root.id})
        self.company_id = self.env.user.company_id
        self.type = self.create_data_range_type("test_hr_period")

        self.vals = {
            "company_id": self.company_id.id,
            "date_start": time.strftime("%Y-01-01"),
            "date_end": time.strftime("%Y-12-31"),
            "schedule_pay": "monthly",
            "type_id": self.type.id,
            "payment_day": "2",
            "payment_weekday": "0",
            "payment_week": "1",
            "name": "Test",
        }
        # create user
        self.user_test = self.user_model.create(
            {
                "name": "User 1",
                "login": "tua@example.com",
                "password": "base-test-passwd",
            }
        )
        # create Employee
        self.employee = self.hr_employee.create(
            {
                "name": "Employee 1",
                "user_id": self.user_test.id,
                "address_id": self.user_test.partner_id.id,
                "parent_id": self.root.id,
                "company_id": self.company_id.id,
            }
        )

    def create_data_range_type(self, name):
        # create Data Range Type
        return self.data_range_type_model.create({"name": name, "active": True})

    def create_fiscal_year(self, vals=None):
        if vals is None:
            vals = {}

        self.vals.update(vals)
        # create Fiscal Year
        return self.fy_model.create(self.vals)

    def get_periods(self, fiscal_year):
        return fiscal_year.period_ids.sorted(key=lambda p: p.date_start)

    def check_period(self, period, date_start, date_end, date_payment):
        if date_start:
            self.assertEqual(period.date_start.strftime("%Y-%m-%d"), date_start)
        if date_end:
            self.assertEqual(period.date_end.strftime("%Y-%m-%d"), date_end)
        if date_payment:
            self.assertEqual(period.date_payment.strftime("%Y-%m-%d"), date_payment)

    def test_create_periods_monthly(self):
        fy = self.create_fiscal_year()
        fy.create_periods()
        periods = self.get_periods(fy)
        self.assertEqual(len(periods), 12)

        self.check_period(
            periods[0],
            time.strftime("%Y-01-01"),
            time.strftime("%Y-01-31"),
            time.strftime("%Y-02-02"),
        )
        current_year = datetime.now().year
        if calendar.isleap(current_year):
            self.check_period(
                periods[1],
                time.strftime("%Y-02-01"),
                time.strftime("%Y-02-29"),
                time.strftime("%Y-03-02"),
            )
        else:
            self.check_period(
                periods[1],
                time.strftime("%Y-02-01"),
                time.strftime("%Y-02-28"),
                time.strftime("%Y-03-02"),
            )
        self.check_period(
            periods[2],
            time.strftime("%Y-03-01"),
            time.strftime("%Y-03-31"),
            time.strftime("%Y-04-02"),
        )
        # the payment is in next year
        self.check_period(
            periods[11],
            time.strftime("%Y-12-01"),
            time.strftime("%Y-12-31"),
            "2025-01-02",
        )

        period_id = self.period_model.search(
            [
                ("date_start", "<=", time.strftime("%Y-%m-11")),
                ("date_end", ">=", time.strftime("%Y-%m-11")),
            ]
        )
        # create HR Period Timesheet
        wizard = self.create_timesheet.with_context(
            active_ids=[period_id.id], active_model="hr.period", active_id=period_id.id
        ).create({})
        wizard.employee_ids = self.employee
        wizard_timesheet = wizard.compute()
        self.assertIn(self.employee.id, wizard.employee_ids.ids)

        timesheet = self.timesheet_sheet.search(
            [
                ("date_start", "=", period_id.date_start),
                ("date_end", "=", period_id.date_end),
                ("company_id", "=", period_id.company_id.id),
            ]
        )
        self.assertEqual(timesheet.employee_id, wizard.employee_ids)
        self.assertEqual(timesheet.id, safe_eval(wizard_timesheet["domain"])[0][2][0])

    def test_create_periods_future(self):
        fy = self.create_fiscal_year()
        fy.create_periods()
        periods = self.get_periods(fy)
        datetime.now().year
        datetime.now().month
        self.env["hr.period.create.timesheet"].create_timesheets_on_future_periods()
        timesheets = self.timesheet_sheet.search(
            [
                ("employee_id", "=", self.employee.id),
                ("date_end", ">", datetime.now()),
                ("company_id", "=", periods[0].company_id.id),
            ]
        )
        periods = self.get_periods(fy)
        last_period = periods[11]
        periods_left = last_period.date_end.month - datetime.now().month + 1
        # timesheets for the rest of the year
        self.assertEqual(len(timesheets), periods_left)
