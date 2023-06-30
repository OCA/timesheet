# © 2016 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, ValidationError

from odoo.addons.hr_holidays.tests.common import TestHrHolidaysCommon
from odoo.addons.mail.tests.common import mail_new_test_user


class TimesheetHolidayTest(TestHrHolidaysCommon):
    def setUp(self):
        super(TimesheetHolidayTest, self).setUp()
        self.leave = self.env["hr.leave"]
        self.project = self.env["project.project"]
        self.sheet = self.env["hr_timesheet.sheet"]
        # grant analytic account access
        self.user_hruser.groups_id += self.env.ref("analytic.group_analytic_accounting")

        self.employee_user = mail_new_test_user(
            self.env, login="Test Emp", groups="base.group_user"
        )
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": self.employee_user.id,
                "department_id": self.rd_dept.id,
            }
        )
        self.sl = self.env.ref("hr_holidays.holiday_status_sl")

    def _create_timesheet(self, employee, date_from, date_to):
        vals = {
            "employee_id": employee.id,
            "date_from": date_from,
            "date_to": date_to,
            "company_id": employee.company_id.id,
            "department_id": employee.department_id.id,
        }
        return self.sheet.create(vals)

    # Create a test customer
    def test_all(self):
        # Working day is 7 hours per day
        self.env.ref("base.main_company").timesheet_hours_per_day = 7.0
        project = self.project.create(
            {
                "name": "Test Project 1",
                "allow_timesheets": False,
            }
        )
        project._create_analytic_account()
        account = project.analytic_account_id
        with self.assertRaises(ValidationError):
            # Create analytic account
            account.write({"is_leave_account": True})
        project.write({"allow_timesheets": True})
        account.write({"is_leave_account": True})
        # Confirm leave and check hours added to account
        hours_before = sum(account.line_ids.mapped("amount"))
        # Holidays.with_user(self.user_employee_id)
        hol_empl_grp = self.leave.with_user(self.user_hruser_id)
        leave = hol_empl_grp.create(
            {
                "name": "One week sick leave",
                "employee_id": self.employee_emp_id,
                "holiday_status_id": self.sl.id,
                "date_from": (datetime.today() - relativedelta(days=7)),
                "date_to": datetime.today(),
            }
        )
        self.assertEqual(
            leave.state,
            "confirm",
            "hr_holidays: newly created leave request should be in " "confirm state",
        )
        leave.with_user(self.user_hruser_id).action_approve()

        hours_after = sum(account.line_ids.mapped("unit_amount"))
        self.assertEqual(hours_after - hours_before, 28.0)

        # Test editing of lines forbidden
        self.assertRaises(
            ValidationError, account.line_ids[0].write, {"unit_amount": 5.0}
        )

        # Test force editing of lines allowed
        account.line_ids[0].with_context(force_write=True).write({"unit_amount": 5.0})
        hours_after = sum(account.line_ids.mapped("unit_amount"))
        self.assertEqual(hours_after - hours_before, 26.0)
        # Ensure the user_id defined on generated analytic lines is the user
        # set on the employee
        user_employee = self.env["hr.employee"].browse(self.employee_emp_id).user_id
        self.assertTrue(user_employee)
        self.assertEqual(account.line_ids.mapped("user_id"), user_employee)
        # Refuse leave and check hours removed from account
        leave.action_refuse()
        hours_final = sum(account.line_ids.mapped("unit_amount"))
        self.assertEqual(hours_final, hours_before)

    def test_timesheet(self):
        # Create analytic account
        project = self.project.create(
            {
                "name": "Personal Leaves",
                "allow_timesheets": True,
            }
        )
        project._create_analytic_account()
        account = project.analytic_account_id
        account.write({"is_leave_account": True})
        # Link sick leave to analytic account
        sl = self.sl
        sl.write({"analytic_account_id": account.id})

        hol_empl_grp = self.leave.with_user(self.user_employee_id)
        leave = hol_empl_grp.create(
            {
                "name": "One week sick leave",
                "employee_id": self.employee_emp_id,
                "holiday_status_id": self.sl.id,
                "date_from": time.strftime("1900-01-06"),
                "date_to": time.strftime("1900-01-12"),
            }
        )
        with self.assertRaises(UserError):
            leave.action_approve()

    def test_allocation(self):
        # Create analytic account
        project = self.project.create(
            {
                "name": "Allocation",
                "allow_timesheets": True,
            }
        )
        project._create_analytic_account()
        account = project.analytic_account_id
        account.write({"is_leave_account": True})
        # Link sick leave to analytic account
        sl = self.sl
        sl.write({"analytic_account_id": account.id})
        leave = self.leave.create(
            {
                "name": "One week sick leave",
                "holiday_status_id": self.sl.id,
                "date_from": time.strftime("%Y-%m-06"),
                "date_to": time.strftime("%Y-%m-12"),
                "employee_id": self.employee.id,
            }
        )
        leave.action_approve()
        self.assertEqual(
            len(leave.analytic_line_ids),
            4,
            "Allocation should not have " "analytic lines",
        )

    def test_timesheet_half_day(self):
        # Test partial day leaves creates timesheet entries
        self.env.ref("base.main_company").timesheet_hours_per_day = 7.0
        project = self.project.create(
            {
                "name": "Test Project 1",
                "allow_timesheets": False,
            }
        )
        project._create_analytic_account()
        account = project.analytic_account_id
        project.write({"allow_timesheets": True})
        account.write({"is_leave_account": True})
        # Confirm leave and check hours added to account
        hours_before = sum(account.line_ids.mapped("amount"))
        # Holidays.with_user(self.user_employee_id)
        hol_empl_grp = self.leave.with_user(self.user_hruser_id)
        leave_date = datetime.today() + (relativedelta(days=10))
        leave = hol_empl_grp.create(
            {
                "name": "One day and a half sick leave",
                "employee_id": self.employee_emp_id,
                "holiday_status_id": self.sl.id,
                "date_from": leave_date - relativedelta(hours=10.5),
                "date_to": leave_date,
            }
        )
        leave.with_user(self.user_hruser_id).action_approve()
        hours_after = sum(account.line_ids.mapped("unit_amount"))
        self.assertEqual(hours_after - hours_before, 3.5)
