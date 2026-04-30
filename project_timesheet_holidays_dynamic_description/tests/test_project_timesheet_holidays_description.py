# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command, fields
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "testeando")
class TestProjectTimesheetHolidaysDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.Employee = cls.env["hr.employee"]
        cls.LeaveType = cls.env["hr.leave.type"]
        cls.Leave = cls.env["hr.leave"]
        cls.AnalyticLine = cls.env["account.analytic.line"]

        cls.Project = cls.env["project.project"]
        cls.Task = cls.env["project.task"]
        cls.Company = cls.env.user.company_id

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
                "company_id": cls.Company.id,
                "allow_timesheets": True,
            }
        )

        cls.task = cls.Task.create(
            {
                "name": "Vacations Task",
                "project_id": cls.project.id,
                "company_id": cls.Company.id,
            }
        )

        cls.Company.write(
            {
                "internal_project_id": cls.project.id,
                "leave_timesheet_task_id": cls.task.id,
                "dynamic_timesheet_description": True,
            }
        )

        cls.employee = cls.Employee.create(
            {
                "name": "Test Employee",
                "user_id": cls.user_employee.id,
                "company_id": cls.Company.id,
            }
        )

        cls.leave_type = cls.LeaveType.create(
            {
                "name": "Leave Test",
                "requires_allocation": "yes",
                "company_id": cls.Company.id,
            }
        )

        cls.allocation = cls.env["hr.leave.allocation"].create(
            {
                "name": "Test Allocation",
                "employee_id": cls.employee.id,
                "holiday_status_id": cls.leave_type.id,
                "number_of_days": 30,
                "state": "confirm",
            }
        )
        cls.allocation._action_validate()

    def _create_leave_with_timesheet(self, days_offset=0):
        self.leave = self.Leave.create(
            {
                "name": "Vacations",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": fields.Date.today(),
                "request_date_to": fields.Date.today(),
            }
        )

        self.leave._action_validate()

        ts = self.AnalyticLine.search([("holiday_id", "=", self.leave.id)], limit=1)

        self.assertTrue(ts)
        return ts

    def test_match_timesheet_and_leave_description(self):
        ts = self._create_leave_with_timesheet(days_offset=1)

        self.assertTrue(
            ts.name.startswith(self.leave.name),
            "The timesheet name should start with the leave description",
        )

    def test_no_match_when_config_disabled(self):
        self.Company.dynamic_timesheet_description = False

        ts = self._create_leave_with_timesheet(days_offset=5)

        self.assertNotIn(
            self.leave.name,
            ts.name,
            "The timesheet name should not contain the "
            "leave name when the config is disabled.",
        )
