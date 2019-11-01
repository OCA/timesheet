# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHrTimesheetRole(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.ResUsers = self.env['res.users']
        self.Company = self.env['res.company']
        self.Project = self.env['project.project']
        self.Role = self.env['project.role']
        self.HrEmployee = self.env['hr.employee']
        self.Assignment = self.env['project.assignment']
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.company_id = self.env['res.company']._company_default_get()
        self.now = fields.Datetime.now()

    def test_defaults(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        project = self.Project.create({
            'name': 'Project',
        })
        role = self.Role.create({
            'name': 'Role',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })
        self.Assignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': employee.user_id.id,
        })
        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'role_id': role.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
        })

    def test_no_required_assignment(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        project = self.Project.create({
            'name': 'Project',
            'limit_role_to_assignments': True,
        })
        role = self.Role.create({
            'name': 'Role',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })

        with self.assertRaises(ValidationError):
            self.AccountAnalyticLine.create({
                'project_id': project.id,
                'role_id': role.id,
                'employee_id': employee.id,
                'name': 'Time Entry',
            })

    def test_no_required_role(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        project = self.Project.create({
            'name': 'Project',
            'limit_role_to_assignments': True,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })

        with self.assertRaises(ValidationError):
            self.AccountAnalyticLine.create({
                'project_id': project.id,
                'employee_id': employee.id,
                'name': 'Time Entry',
            })

    def test_no_role_allowed(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        project = self.Project.create({
            'name': 'Project',
            'is_timesheet_role_required': False,
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })

        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
        })

    def test_no_assignment_allowed(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        project = self.Project.create({
            'name': 'Project',
            'company_id': self.company_id.id,
        })
        role = self.Role.create({
            'name': 'Role',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })

        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'role_id': role.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
        })

    def test_change_project(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        project_1 = self.Project.create({
            'name': 'Project 1',
            'limit_role_to_assignments': True,
        })
        project_2 = self.Project.create({
            'name': 'Project 2',
            'limit_role_to_assignments': True,
        })
        role_1 = self.Role.create({
            'name': 'Role 1',
        })
        role_2 = self.Role.create({
            'name': 'Role 2',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': user.id,
        })
        self.Assignment.create({
            'project_id': project_1.id,
            'role_id': role_1.id,
            'user_id': user.id,
        })
        self.Assignment.create({
            'project_id': project_2.id,
            'role_id': role_2.id,
            'user_id': user.id,
        })
        account_analytic_line = self.AccountAnalyticLine.create({
            'project_id': project_1.id,
            'role_id': role_1.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
        })

        with common.Form(
                account_analytic_line,
                view='hr_timesheet.timesheet_view_form_user') as form:
            form.project_id = project_2
            self.assertFalse(form.role_id)
            form.role_id = role_2

    def test_creation_defaults(self):
        user = self.ResUsers.sudo().create({
            'name': 'User',
            'login': 'user',
            'email': 'user@example.com',
            'company_id': self.company_id.id,
        })
        role = self.Role.create({
            'name': 'Role',
        })
        company = self.Company.create({
            'name': 'Company',
            'is_timesheet_role_required': False,
            'project_limit_role_to_assignments': True,
        })
        project = self.Project.create({
            'name': 'Project',
            'company_id': company.id,
        })
        employee = self.HrEmployee.create({
            'company_id': company.id,
            'name': 'Employee',
            'user_id': user.id,
        })
        self.Assignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': employee.user_id.id,
        })
        self.assertEqual(
            project.company_id.id,
            company.id
        )
        self.assertEqual(
            project.is_timesheet_role_required,
            company.is_timesheet_role_required
        )

        account_analytic_line = self.AccountAnalyticLine.create({
            'company_id': company.id,
            'project_id': project.id,
            'role_id': role.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
        })
        account_analytic_line._onchange_project_or_employee()
