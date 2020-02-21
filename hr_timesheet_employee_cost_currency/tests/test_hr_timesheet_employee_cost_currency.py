# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrTimesheetEmployeeCostCurrency(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.HrEmployee = self.env['hr.employee']
        self.eur = self.env.ref('base.EUR')

    def test_defaults(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })

        self.assertEqual(employee.currency_id, employee.company_id.currency_id)

    def test_specific(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'currency_id': self.eur.id,
        })

        self.assertEqual(employee.currency_id, self.eur)
