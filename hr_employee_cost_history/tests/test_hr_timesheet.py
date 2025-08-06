# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import date

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.tests import Form, TransactionCase, new_test_user, users


@freeze_time("2024-02-23", tick=True)
class HrEmployeeCostHistory(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_plan = cls.env["account.analytic.plan"].create({"name": "Default"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Account for Test Customer",
                "code": "TEST",
                "plan_id": cls.default_plan.id,
            }
        )
        # users
        new_test_user(
            cls.env,
            login="test_user_manager",
            groups="hr_timesheet.group_timesheet_manager",
        )
        cls.user_employee = new_test_user(
            cls.env,
            login="test_user_employee",
            groups="hr_timesheet.group_hr_timesheet_user",
        )
        # employee
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "User Empl Employee",
                "hourly_cost": 10.0,
                "user_id": cls.user_employee.id,
            }
        )
        # project and tasks
        cls.project_customer = cls.env["project.project"].create(
            {
                "name": "Project X",
                "allow_timesheets": True,
                "account_id": cls.analytic_account.id,
                "company_id": False,
            }
        )
        cls.task1 = cls.env["project.task"].create(
            {
                "name": "Task One",
                "priority": "0",
                "state": "01_in_progress",
                "project_id": cls.project_customer.id,
            }
        )
        cls.task2 = cls.env["project.task"].create(
            {
                "name": "Task Two",
                "priority": "1",
                "state": "03_approved",
                "project_id": cls.project_customer.id,
            }
        )
        # timesheets
        cls.timesheets = cls.env["account.analytic.line"].create(
            [
                {
                    "project_id": cls.project_customer.id,
                    "task_id": cls.task1.id,
                    "name": "Timesheet 1",
                    "unit_amount": 4,
                    "user_id": cls.user_employee.id,
                    "employee_id": cls.employee.id,
                    "date": date.today() - relativedelta(days=5),
                },
                {
                    "project_id": cls.project_customer.id,
                    "task_id": cls.task1.id,
                    "name": "Timesheet 2",
                    "unit_amount": 3,
                    "user_id": cls.user_employee.id,
                    "employee_id": cls.employee.id,
                    "date": date.today() - relativedelta(days=3),
                },
                {
                    "project_id": cls.project_customer.id,
                    "task_id": cls.task2.id,
                    "name": "Timesheet 3",
                    "unit_amount": 2,
                    "user_id": cls.user_employee.id,
                    "employee_id": cls.employee.id,
                    "date": date.today() - relativedelta(days=1),
                },
            ]
        )

    def new_timesheet_cost_wizard(self, employee, cost, date_from):
        """Create a new wizard for this test's employee."""
        wizard = Form(
            self.env["hr.employee.timesheet.cost.wizard"].with_context(
                default_employee_id=employee.id,
                default_hourly_cost=cost,
                default_starting_date=date_from,
            )
        )
        wizard_result = wizard.save()
        wizard_result.update_employee_cost()

    @users("test_user_manager")
    def test_update_employee_cost_change(self):
        """Test modify employee's costs."""
        old_cost = sum(
            self.env["account.analytic.line"]
            .search([("project_id", "=", self.project_customer.id)])
            .mapped("amount")
        )
        old_cost = self.env["account.analytic.line"].read_group(
            [("project_id", "=", self.project_customer.id)],
            ["amount"],
            ["project_id"],
        )[0]["amount"]
        self.assertEqual(old_cost, -90.0)
        self.new_timesheet_cost_wizard(
            self.employee, 15.0, date.today() - relativedelta(days=2)
        )
        new_cost = sum(
            self.env["account.analytic.line"]
            .search([("project_id", "=", self.project_customer.id)])
            .mapped("amount")
        )
        self.assertEqual(new_cost, -100.0)
        self.new_timesheet_cost_wizard(
            self.employee, 20.0, date.today() - relativedelta(days=4)
        )
        new_cost = sum(
            self.env["account.analytic.line"]
            .search([("project_id", "=", self.project_customer.id)])
            .mapped("amount")
        )
        self.assertEqual(new_cost, -140.0)
        self.new_timesheet_cost_wizard(
            self.employee, 20.0, date.today() - relativedelta(days=5)
        )
        new_cost = sum(
            self.env["account.analytic.line"]
            .search([("project_id", "=", self.project_customer.id)])
            .mapped("amount")
        )
        self.assertEqual(new_cost, -180.0)

    @users("test_user_manager")
    def test_update_employee_history_cost(self):
        """Test employee history cost is consistent when dates overlap."""
        # days ago when the cost was changed
        days_history_cost = [15, 10, 5, 1]
        for days in days_history_cost:
            self.new_timesheet_cost_wizard(
                self.employee, 15.0, date.today() - relativedelta(days=days)
            )
        # overlap the last two cost changes
        self.new_timesheet_cost_wizard(
            self.employee, 15.0, date.today() - relativedelta(days=7)
        )
        new_days_history_cost = [15, 10, 7]
        timesheet_cost_ids = self.env["hr.employee.timesheet.cost.history"].search(
            [
                ("employee_id", "=", self.employee.id),
            ]
        )
        self.assertEqual(len(timesheet_cost_ids), len(new_days_history_cost))
        for timesheet_cost, days in zip(
            timesheet_cost_ids, new_days_history_cost, strict=False
        ):
            self.assertEqual(
                timesheet_cost.starting_date,
                date.today() - relativedelta(days=days),
            )
        # modify same day but change cost
        self.new_timesheet_cost_wizard(
            self.employee, 20.0, date.today() - relativedelta(days=7)
        )
        timesheet_cost_ids = self.env["hr.employee.timesheet.cost.history"].search(
            [
                ("employee_id", "=", self.employee.id),
            ]
        )
        self.assertEqual(len(timesheet_cost_ids), len(new_days_history_cost))
        for timesheet_cost, days in zip(
            timesheet_cost_ids, new_days_history_cost, strict=False
        ):
            self.assertEqual(
                timesheet_cost.starting_date,
                date.today() - relativedelta(days=days),
            )
        last_timesheet = timesheet_cost_ids[-1]
        self.assertEqual(last_timesheet.hourly_cost, 20.0)

    @users("test_user_manager")
    def test_field_comment(self):
        """Test comment field."""
        wizard = Form(
            self.env["hr.employee.timesheet.cost.wizard"].with_context(
                default_employee_id=self.employee.id,
                default_hourly_cost=123,
                default_starting_date=date.today(),
                default_comment="Test comment",
            )
        )
        wizard_result = wizard.save()
        wizard_result.update_employee_cost()
        comment = (
            self.env["hr.employee.timesheet.cost.history"]
            .search(
                [
                    ("employee_id", "=", self.employee.id),
                    ("hourly_cost", "=", 123),
                ]
            )
            .comment
        )
        self.assertEqual(comment, "Test comment")
