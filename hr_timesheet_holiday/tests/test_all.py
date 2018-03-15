# -*- coding: utf-8 -*-
# © 2016 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TimesheetHolidayTest(TransactionCase):
    def setUp(self):
        super(TimesheetHolidayTest, self).setUp()
        self.leave = self.env['hr.holidays']
        self.account = self.env['account.analytic.account']

    # Create a test customer
    def test_all(self):
        # Working day is 7 hours per day
        self.env.ref('base.main_company') \
            .timesheet_hours_per_day = 7.0

        # Create analytic account
        account = self.account.create({
            'name': 'Sick Leaves',
            'is_leave_account': True
        })

        # Link sick leave to analytic account
        sl = self.env.ref('hr_holidays.holiday_status_sl')
        sl.write({
            'analytic_account_id': account.id
        })

        # Create sick leave for Pieter Parker
        leave = self.leave.create({
            'name': 'One week sick leave',
            'holiday_status_id': sl.id,
            'date_from': time.strftime('%Y-%m-06'),
            'date_to': time.strftime('%Y-%m-12'),
            'number_of_days_temp': 7.0,
            'employee_id': self.env.ref('hr.employee_fp').id,
        })

        # Confirm leave and check hours added to account
        hours_before = sum(account.line_ids.mapped('amount'))
        leave.signal_workflow('confirm')
        leave.signal_workflow('validate')
        leave.signal_workflow('second_validate')
        hours_after = sum(account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_after - hours_before, 35.0)

        # Test editing of lines forbidden
        self.assertRaises(ValidationError, account.line_ids[0].write, {
            'unit_amount': 5.0
        })

        # Test force editing of lines allowed
        account.line_ids[0].with_context(force_write=True).write({
            'unit_amount': 5.0
        })
        hours_after = sum(account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_after - hours_before, 33.0)

        # Refuse leave and check hours removed from account
        leave.signal_workflow('refuse')
        hours_final = sum(account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_final, hours_before)
