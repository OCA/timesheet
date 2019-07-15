# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHrTimesheetRole(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.now = fields.Datetime.now()
        self.Company = self.env['res.company']
        self.SudoCompany = self.Company.sudo()
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.Role = self.env['project.role']
        self.SudoRole = self.Role.sudo()
        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.Assignment = self.env['project.assignment']
        self.SudoAssignment = self.Assignment.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.HrTimesheetSheet = self.env['hr_timesheet.sheet']
        self.SudoHrTimesheetSheet = self.HrTimesheetSheet.sudo()

    def test_1(self):
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        role = self.SudoRole.create({
            'name': 'Role #1',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #1',
            'user_id': self.env.user.id,
        })
        self.SudoAssignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': employee.user_id.id,
        })
        sheet = self.SudoHrTimesheetSheet.create({
            'employee_id': employee.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        sheet.add_line_project_id = project
        sheet.onchange_add_project_id()
        sheet.add_line_role_id = role
        sheet.button_add_line()
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

        sheet.date_end = sheet.date_end + relativedelta(days=1)
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

    def test_2(self):
        company = self.SudoCompany.create({
            'name': 'Company #2',
            'is_timesheet_role_required': False,
            'limit_timesheet_role_to_assignments': True,
        })
        project = self.SudoProject.create({
            'name': 'Project #2',
        })
        role = self.SudoRole.create({
            'name': 'Role #2',
            'company_id': company.id,
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #2',
            'user_id': self.env.user.id,
        })
        self.SudoAssignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': employee.user_id.id,
        })
        sheet = self.SudoHrTimesheetSheet.create({
            'employee_id': employee.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        sheet.add_line_project_id = project
        sheet.onchange_add_project_id()

        with self.assertRaises(ValidationError):
            sheet.add_line_role_id = role

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
            'limit_timesheet_role_to_assignments': True,
        })
        role = self.SudoRole.create({
            'name': 'Role #3',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #3',
            'user_id': self.env.user.id,
        })
        self.SudoAssignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': employee.user_id.id,
        })
        sheet = self.SudoHrTimesheetSheet.create({
            'employee_id': employee.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        sheet.add_line_project_id = project
        sheet.onchange_add_project_id()
        sheet.add_line_role_id = role
        sheet.button_add_line()
