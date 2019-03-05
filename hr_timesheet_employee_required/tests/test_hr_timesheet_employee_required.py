# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestHrTimesheetEmployeeRequired(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.main_company = self.env.ref('base.main_company')
        self.group_hr_timesheet_user = self.ref(
            'hr_timesheet.group_hr_timesheet_user'
        )
        self.now = fields.Datetime.now()
        self.User = self.env['res.users']
        self.SudoUser = self.User.sudo()
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()

    def test_1(self):
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        user = self.SudoUser.create({
            'name': 'User #1',
            'login': 'test_hr_timesheet_employee_required_1',
            'email': 'user-1@localhost',
            'company_id': self.main_company.id,
            'groups_id': [(6, 0, [
                self.group_hr_timesheet_user,
            ])]
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.AccountAnalyticLine.sudo(user=user).create({
                'project_id': project.id,
                'name': 'Time Entry #1',
            })

    def test_2(self):
        project = self.SudoProject.create({
            'name': 'Project #2',
        })
        user = self.SudoUser.create({
            'name': 'User #2',
            'login': 'test_hr_timesheet_employee_required_2',
            'email': 'user-2@localhost',
            'company_id': self.main_company.id,
            'groups_id': [(6, 0, [
                self.group_hr_timesheet_user,
            ])]
        })
        self.SudoHrEmployee.create({
            'name': 'Employee #2',
            'user_id': user.id,
        })

        self.AccountAnalyticLine.sudo(user=user).create({
            'project_id': project.id,
            'name': 'Time Entry #2',
        })

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #3',
        })

        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #3',
            'employee_id': employee.id,
        })
