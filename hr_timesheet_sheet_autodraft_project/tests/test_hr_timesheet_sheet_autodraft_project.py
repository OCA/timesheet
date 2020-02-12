# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrTimesheetSheetAutodraftProject(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.ResUsers = self.env['res.users']
        self.Company = self.env['res.company']
        self.Project = self.env['project.project']
        self.HrEmployee = self.env['hr.employee']
        self.HrTimesheetSheet = self.env['hr_timesheet.sheet']
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.company_id = self.Company._company_default_get()

    def test_autocreate(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })
        project = self.Project.create({
            'name': 'Project',
        })

        self.company_id.timesheet_sheets_autodraft = True
        self.company_id.timesheet_sheet_review_policy = 'project_manager'
        aal = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
        })

        self.assertEquals(aal.sheet_id.project_id, project)
