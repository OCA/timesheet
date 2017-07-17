# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from datetime import datetime
from odoo.exceptions import ValidationError as UserError


class TestHrTimesheetSheetPeriod(common.TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheetPeriod, self).setUp()
        self.timeheet_model = self.env['hr_timesheet_sheet.sheet']
        self.fiscal_year_model = self.env['hr.fiscalyear']
        self.hr_contract_model = self.env['hr.contract']

        self.today_date = datetime.today().date()
        self.date_start = datetime.today().strftime('%Y-01-01')
        self.date_stop = datetime.today().strftime('%Y-12-31')
        self.company = self.env.ref('base.main_company')
        self.employee = self.env.ref('hr.employee_root')

    def create_fiscal_year(self):
        vals = {
            'company_id': self.company.id,
            'date_start': self.date_start,
            'date_stop': self.date_stop,
            'schedule_pay': 'monthly',
            'payment_day': '2',
            'name': 'Test Fiscal Year 2017',
        }

        fiscal_year = self.fiscal_year_model.create(vals)

        return fiscal_year

    def create_hr_timesheet_sheet(self):
        timesheet_sheet = self.timeheet_model.create({
            'employee_id': self.employee.id
        })
        return timesheet_sheet

    def test_hr_timesheet_period(self):
        fiscal_year = self.create_fiscal_year()
        fiscal_year.create_periods()
        fiscal_year.button_confirm()
        hr_timesheet = self.create_hr_timesheet_sheet()
        self.assertEqual(hr_timesheet.hr_period_id.date_start,
                         hr_timesheet.date_from)
        self.assertEqual(hr_timesheet.hr_period_id.date_stop,
                         hr_timesheet.date_to)
        self.assertEqual(self.today_date.month,
                         hr_timesheet.hr_period_id.number)
        hr_timesheet.onchange_pay_period()
        with self.assertRaises(UserError):
            hr_timesheet.date_from = '2017-12-31'
        with self.assertRaises(UserError):
            hr_timesheet.date_to = '2017-12-31'

    def test_period_from_employee_contract(self):
        fiscal_year = self.create_fiscal_year()
        fiscal_year.create_periods()
        fiscal_year.button_confirm()
        hr_timesheet = self.create_hr_timesheet_sheet()
        salary_structure = self.env.ref('hr_payroll.structure_001')

        contract_vals = {
            'employee_id': self.employee.id,
            'struct_id': salary_structure.id,
            'schedule_pay': 'monthly',
            'name': 'Test Contract',
            'wage': 20000
        }

        hr_contract = self.hr_contract_model.create(contract_vals)

        self.assertEqual(hr_timesheet.hr_period_id.date_start,
                         hr_timesheet.date_from)
        self.assertEqual(hr_timesheet.hr_period_id.date_stop,
                         hr_timesheet.date_to)
        self.assertEqual(self.today_date.month,
                         hr_timesheet.hr_period_id.number)
        self.assertEqual(hr_contract.schedule_pay,
                         hr_timesheet.hr_period_id.schedule_pay)
        with self.assertRaises(UserError):
            hr_timesheet.date_to = '2017-12-31'
