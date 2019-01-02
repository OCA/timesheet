# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common

from dateutil.relativedelta import relativedelta


class TestHrUtilizationAnalysis(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.Wizard = self.env['hr.utilization.analysis.wizard']
        self.Analysis = self.env['hr.utilization.analysis']

    def test_1(self):
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #1-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #1-2',
            'active': False,
        })
        employee_3 = self.SudoHrEmployee.create({
            'name': 'Employee #1-3',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #1-1',
            'employee_id': employee_1.id,
            'date': self.today,
            'unit_amount': 4,
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #1-2',
            'employee_id': employee_1.id,
            'date': self.today - relativedelta(days=1),
            'unit_amount': 4,
        })

        wizard = self.Wizard.create({
            'date_from': self.today,
            'date_to': self.today,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
                employee_3.id,
            ])],
        })
        wizard.action_view()

        analysis = self.Analysis.create(
            wizard._collect_analysis_values()
        )
        self.assertEqual(len(analysis.entry_ids), 2)
