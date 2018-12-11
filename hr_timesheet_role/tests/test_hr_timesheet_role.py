# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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

        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'role_id': role.id,
            'employee_id': employee.id,
            'name': 'Time Entry #1',
        })

    def test_2(self):
        project = self.SudoProject.create({
            'name': 'Project #2',
            'limit_timesheet_role_to_assignments': True,
        })
        role = self.SudoRole.create({
            'name': 'Role #2',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #2',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(ValidationError):
            self.SudoAccountAnalyticLine.create({
                'project_id': project.id,
                'role_id': role.id,
                'employee_id': employee.id,
                'name': 'Time Entry #2',
            })

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
            'limit_timesheet_role_to_assignments': True,
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #3',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(ValidationError):
            self.SudoAccountAnalyticLine.create({
                'project_id': project.id,
                'employee_id': employee.id,
                'name': 'Time Entry #3',
            })

    def test_4(self):
        project = self.SudoProject.create({
            'name': 'Project #4',
            'is_timesheet_role_required': False,
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #4',
            'user_id': self.env.user.id,
        })

        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry #4',
        })

    def test_5(self):
        project = self.SudoProject.create({
            'name': 'Project #5',
            'company_id': self.env.user.company_id.id,
        })
        role = self.SudoRole.create({
            'name': 'Role #5',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #5',
            'user_id': self.env.user.id,
        })

        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'role_id': role.id,
            'employee_id': employee.id,
            'name': 'Time Entry #5',
        })

    def test_6(self):
        project_1 = self.SudoProject.create({
            'name': 'Project #6-1',
            'limit_timesheet_role_to_assignments': False,
        })
        project_2 = self.SudoProject.create({
            'name': 'Project #6-2',
            'limit_timesheet_role_to_assignments': False,
        })
        role_1 = self.SudoRole.create({
            'name': 'Role #6-1',
        })
        role_2 = self.SudoRole.create({
            'name': 'Role #6-2',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #6',
            'user_id': self.env.user.id,
        })
        self.SudoAssignment.create({
            'project_id': project_1.id,
            'role_id': role_1.id,
            'user_id': employee.user_id.id,
        })
        self.SudoAssignment.create({
            'project_id': project_2.id,
            'role_id': role_2.id,
            'user_id': employee.user_id.id,
        })
        account_analytic_line = self.SudoAccountAnalyticLine.create({
            'project_id': project_1.id,
            'role_id': role_1.id,
            'employee_id': employee.id,
            'name': 'Time Entry #6',
        })

        account_analytic_line.project_id = project_2
        account_analytic_line._onchange_project_or_employee()
        self.assertEqual(account_analytic_line.role_id.id, False)

    def test_7(self):
        role = self.SudoRole.create({
            'name': 'Role #7',
        })
        company = self.SudoCompany.create({
            'name': 'Company #7',
            'is_timesheet_role_required': False,
            'limit_timesheet_role_to_assignments': True,
        })
        project = self.SudoProject.create({
            'name': 'Project #7',
            'company_id': company.id,
        })
        employee = self.SudoHrEmployee.create({
            'company_id': company.id,
            'name': 'Employee #6',
            'user_id': self.env.user.id,
        })
        self.SudoAssignment.create({
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
        self.assertEqual(
            project.limit_timesheet_role_to_assignments,
            company.limit_timesheet_role_to_assignments
        )

        account_analytic_line = self.SudoAccountAnalyticLine.create({
            'company_id': company.id,
            'project_id': project.id,
            'role_id': role.id,
            'employee_id': employee.id,
            'name': 'Time Entry #6',
        })
        account_analytic_line._onchange_project_or_employee()
