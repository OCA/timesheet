# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrTimesheetNonpayable(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.Project = self.env['project.project']
        self.HrEmployee = self.env['hr.employee']
        self.AccountAnalyticLine = self.env['account.analytic.line']

    def test_create_common(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'timesheet_cost': 10.0,
        })
        aal = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
            'unit_amount': 1.0,
        })
        self.assertEqual(aal.amount, -10.0)
        self.assertEqual(aal.nonpayable_amount, 0.0)
        self.assertFalse(aal.is_nonpayable)

    def test_create_nonpayable(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'timesheet_cost': 10.0,
        })
        aal = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
            'unit_amount': 1.0,
            'is_nonpayable': True,
        })
        self.assertEqual(aal.amount, 0.0)
        self.assertEqual(aal.nonpayable_amount, -10.0)
        self.assertTrue(aal.is_nonpayable)

    def test_payable_to_nonpayable_to_payable(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'timesheet_cost': 10.0,
        })
        aal = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
            'unit_amount': 1.0,
        })

        aal.is_nonpayable = True
        self.assertEqual(aal.amount, 0.0)
        self.assertEqual(aal.nonpayable_amount, -10.0)

        aal.is_nonpayable = False
        self.assertEqual(aal.amount, -10.0)
        self.assertEqual(aal.nonpayable_amount, 0.0)

    def test_nonpayable_to_payable_to_nonpayable(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'timesheet_cost': 10.0,
        })
        aal = self.AccountAnalyticLine.create({
            'project_id': project.id,
            'employee_id': employee.id,
            'name': 'Time Entry',
            'unit_amount': 1.0,
            'is_nonpayable': True,
        })

        aal.is_nonpayable = False
        self.assertEqual(aal.amount, -10.0)
        self.assertEqual(aal.nonpayable_amount, 0.0)

        aal.is_nonpayable = True
        self.assertEqual(aal.amount, 0.0)
        self.assertEqual(aal.nonpayable_amount, -10.0)
