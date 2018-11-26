# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrTimesheetEmployeeUser(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()

    def test_1(self):
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #1',
        })
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        line = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Test #1',
        })

        line._onchange_employee_id()
        self.assertEqual(line.user_id.id, False)

        employee.user_id = self.env.user
        line._reset_user_from_employee()
        self.assertEqual(line.user_id.id, self.env.user.id)
