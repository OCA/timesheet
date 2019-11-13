# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from datetime import date
from odoo.exceptions import ValidationError

from ..models.res_company import SHEET_RANGE_PAYROLL_PERIOD


class TestHrTimesheetSheetPeriod(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.HrTimesheetSheet = self.env['hr_timesheet.sheet']
        self.HrFiscalYear = self.env['hr.fiscalyear']
        self.HrContract = self.env['hr.contract']
        self.DateRangeType = self.env['date.range.type']

        self.today_date = date.today()
        self.date_start = self.today_date.strftime('%Y-01-01')
        self.date_end = self.today_date.strftime('%Y-12-31')
        self.company = self.env.ref('base.main_company')
        self.employee = self.env.ref('hr.employee_admin')

        self.company.sheet_range = SHEET_RANGE_PAYROLL_PERIOD
        self.fiscal_year_date_range_type = self.DateRangeType.create({
            'name': 'Fiscal year',
            'allow_overlap': False
        })

    def _create_fiscal_year(self):
        return self.HrFiscalYear.create({
            'company_id': self.company.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'schedule_pay': 'monthly',
            'payment_day': '2',
            'name': 'Test Fiscal Year 2018',
            'type_id': self.fiscal_year_date_range_type.id,
        })

    def _create_hr_timesheet_sheet(self):
        return self.HrTimesheetSheet.create({
            'employee_id': self.employee.id,
        })

    def test_no_period(self):
        self._create_fiscal_year()
        with self.assertRaises(ValidationError):
            self._create_hr_timesheet_sheet()

    def test_hr_timesheet_period(self):
        fiscal_year = self._create_fiscal_year()
        fiscal_year.create_periods()
        fiscal_year.button_confirm()
        hr_timesheet = self._create_hr_timesheet_sheet()
        self.assertEqual(hr_timesheet.hr_period_id.date_start,
                         hr_timesheet.date_start)
        self.assertEqual(hr_timesheet.hr_period_id.date_end,
                         hr_timesheet.date_end)
        self.assertEqual(self.today_date.month,
                         hr_timesheet.hr_period_id.number)
        hr_timesheet._onchange_employee_hr_period_id()
        with self.assertRaises(ValidationError):
            hr_timesheet.date_start = '2018-12-31'
        with self.assertRaises(ValidationError):
            hr_timesheet.date_end = '2018-12-31'

    def test_period_from_employee_contract(self):
        fiscal_year = self._create_fiscal_year()
        fiscal_year.create_periods()
        fiscal_year.button_confirm()
        hr_timesheet = self._create_hr_timesheet_sheet()
        salary_structure = self.env.ref('hr_payroll.structure_001')

        contract_vals = {
            'employee_id': self.employee.id,
            'struct_id': salary_structure.id,
            'schedule_pay': 'monthly',
            'name': 'Test Contract',
            'wage': 20000
        }

        hr_contract = self.HrContract.create(contract_vals)

        self.assertEqual(hr_timesheet.hr_period_id.date_start,
                         hr_timesheet.date_start)
        self.assertEqual(hr_timesheet.hr_period_id.date_end,
                         hr_timesheet.date_end)
        self.assertEqual(self.today_date.month,
                         hr_timesheet.hr_period_id.number)
        self.assertEqual(hr_contract.schedule_pay,
                         hr_timesheet.hr_period_id.schedule_pay)
        self.assertEqual(hr_timesheet.name, hr_timesheet.hr_period_id.name)
        with self.assertRaises(ValidationError):
            hr_timesheet.date_end = '2018-03-31'
