# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrTimesheetSheetAutodraft(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.ResUsers = self.env["res.users"]
        self.Company = self.env["res.company"]
        self.Project = self.env["project.project"]
        self.HrEmployee = self.env["hr.employee"]
        self.HrTimesheetSheet = self.env["hr_timesheet.sheet"]
        self.AccountAnalyticLine = self.env["account.analytic.line"]
        self.company_id = self.env.company

    def test_no_autocreate_by_default(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        aal = self.AccountAnalyticLine.create(
            {"project_id": project.id, "employee_id": employee.id, "name": "Time Entry"}
        )

        self.assertFalse(aal.sheet_id)

    def test_autocreate(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        aal_1 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 1",
            }
        )

        self.company_id.timesheet_sheets_autodraft = True

        aal_2 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 2",
            }
        )

        self.assertTrue(aal_1.sheet_id)
        self.assertTrue(aal_2.sheet_id)
        self.assertEqual(aal_1.sheet_id, aal_2.sheet_id)

    def test_already_confirmed(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        self.company_id.timesheet_sheets_autodraft = True

        aal_1 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 1",
            }
        )

        aal_1.sheet_id.with_user(user).action_timesheet_confirm()

        aal_2 = self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry 2",
            }
        )
        self.assertFalse(aal_2.sheet_id)

    def test_repeated_auto_draft(self):
        user = self.ResUsers.sudo().create(
            {
                "name": "User",
                "login": "user",
                "email": "user@example.com",
                "company_id": self.company_id.id,
            }
        )
        employee = self.HrEmployee.create({"name": "Employee", "user_id": user.id})
        project = self.Project.create({"name": "Project"})

        self.company_id.timesheet_sheets_autodraft = True

        aal = self.AccountAnalyticLine.create(
            {"project_id": project.id, "employee_id": employee.id, "name": "Time Entry"}
        )
        sheet = aal.sheet_id

        aal.sheet_id.with_user(user).action_timesheet_confirm()

        aal.action_autodraft_timesheet_sheets()

        self.assertEqual(aal.sheet_id, sheet)
