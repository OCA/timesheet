# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from datetime import date

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install", "pruebilla")
class TestProjectTimesheetHolidays(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Employee = cls.env["hr.employee"]
        cls.LeaveType = cls.env["hr.leave.type"]
        cls.Leave = cls.env["hr.leave"]
        cls.AnalyticLine = cls.env["account.analytic.line"]
        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]

        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "HR Employee",
                "login": "hr_employee",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("hr_timesheet.group_hr_timesheet_user").id,
                        ]
                    )
                ],
            }
        )

        cls.user_approver = cls.env["res.users"].create(
            {
                "name": "HR Approver",
                "login": "hr_approver",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("hr_holidays.group_hr_holidays_user").id,
                            cls.env.ref("project.group_project_manager").id,
                        ]
                    )
                ],
            }
        )

        cls.project = cls.Project.create(
            {
                "name": "Project Vacations",
                "company_id": cls.env.company.id,
            }
        )

        cls.task = cls.Task.create(
            {
                "name": "Vacations Task",
                "project_id": cls.project.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.env.company.write(
            {
                "internal_project_id": cls.project.id,
                "leave_timesheet_task_id": cls.task.id,
            }
        )

        cls.employee = cls.Employee.create(
            {
                "name": "Test Employee",
                "user_id": cls.user_employee.id,
                "company_id": cls.env.company.id,
            }
        )

    def _create_leave_with_timesheet(self, edit_level):
        self.employee.company_id.write(
            {
                "timesheet_edit_level": edit_level,
            }
        )

        leave_type = self.LeaveType.create(
            {
                "name": f"Leave {edit_level}",
            }
        )

        allocation = self.env["hr.leave.allocation"].create(
            {
                "name": "Test Allocation",
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "number_of_days": 10,
            }
        )
        allocation.action_approve()

        leave = self.Leave.create(
            {
                "name": "Vacations",
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "request_date_from": date.today(),
                "request_date_to": date.today(),
            }
        )

        leave.action_approve()

        ts = self.AnalyticLine.search([("holiday_id", "=", leave.id)], limit=1)

        self.assertTrue(ts)
        return ts

    def test_edit_timesheet_allowed_edit_level_all(self):
        ts = self._create_leave_with_timesheet("all")

        ts.with_user(self.user_employee).write(
            {
                "name": "New name",
                "unit_amount": 4,
            }
        )

    def test_edit_timesheet_not_allowed_edit_level_all(self):
        ts = self._create_leave_with_timesheet("all")

        with self.assertRaises(UserError):
            ts.with_user(self.user_employee).write(
                {
                    "date": date.today(),
                }
            )

    def test_edit_timesheet_not_allowed_edit_level_none(self):
        ts = self._create_leave_with_timesheet("none")

        with self.assertRaises(UserError):
            ts.with_user(self.user_employee).write(
                {
                    "name": "shouldnt be able",
                }
            )

    def test_edit_timesheet_by_employee_without_group_edit_level_approver(self):
        ts = self._create_leave_with_timesheet("approver")

        with self.assertRaises(UserError):
            ts.with_user(self.user_employee).write(
                {
                    "unit_amount": 3,
                }
            )

    def test_edit_timesheet_by_user_approver_without_group_edit_level_approver(self):
        ts = self._create_leave_with_timesheet("approver")

        ts.with_user(self.user_approver).write(
            {
                "unit_amount": 3,
            }
        )
