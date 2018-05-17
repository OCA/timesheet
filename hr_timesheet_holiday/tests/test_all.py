# -*- coding: utf-8 -*-
# © 2016 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import time
from openerp.tests.common import TransactionCase
from openerp.exceptions import ValidationError


class TimesheetHolidayTest(TransactionCase):
    def setUp(self):
        super(TimesheetHolidayTest, self).setUp()
        # Working day is 7 hours per day
        self.env.ref('base.main_company') \
            .timesheet_hours_per_day = 7.0

        # Create analytic account
        self.account = self.env['account.analytic.account'].create({
            'name': 'Sick Leaves',
            'is_leave_account': True,
            'type': 'normal',
        })

        # Link sick leave to analytic account
        self.sl = self.env.ref('hr_holidays.holiday_status_sl')
        self.sl.write({
            'analytic_account_id': self.account.id
        })

    def test_leave(self):
        # Create sick leave for Pieter Parker
        leave = self.env['hr.holidays'].create({
            'name': 'One week sick leave',
            'holiday_status_id': self.sl.id,
            'date_from': time.strftime('%Y-%m-06'),
            'date_to': time.strftime('%Y-%m-12'),
            'number_of_days_temp': 7.0,
            'employee_id': self.env.ref('hr.employee_fp').id,
        })

        # Confirm leave and check hours added to account
        hours_before = sum(self.account.line_ids.mapped('amount'))
        leave.signal_workflow('confirm')
        leave.signal_workflow('validate')
        leave.signal_workflow('second_validate')
        hours_after = sum(self.account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_after - hours_before, 35.0)

        # Test editing of lines forbidden
        self.assertRaises(ValidationError, self.account.line_ids[0].write, {
            'unit_amount': 5.0
        })

        # Test force editing of lines allowed
        self.account.line_ids[0].with_context(force_write=True).write({
            'unit_amount': 5.0
        })
        hours_after = sum(self.account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_after - hours_before, 33.0)

        # Refuse leave and check hours removed from account
        leave.signal_workflow('refuse')
        hours_final = sum(self.account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_final, hours_before)

    def test_analytic(self):
        manager = self.env.ref('hr.employee_fp')
        employee = self.env.ref('hr.employee_qdp')
        employee.write(employee.default_get(['product_id', 'journal_id']))

        # create timesheet line with 6.0 hours of sick leave
        line = self.env['hr.analytic.timesheet'].sudo(
            employee.user_id,
        ).default_get([
            'general_account_id', 'journal_id', 'name', 'product_id',
            'product_uom_id',
        ])
        line.update(self.env['hr.analytic.timesheet'].on_change_account_id(
            self.account.id, employee.user_id.id
        )['value'])
        line.update(
            account_id=self.account.id,
            date=time.strftime('%Y-%m-06'),
            name='/',
            unit_amount=6,
        )

        # create and confirm a timesheet with the 6.0 hours line
        sheet = self.env['hr_timesheet_sheet.sheet'].sudo(
            employee.user_id
        ).create({
            'employee_id': employee.id,
            'date_from': time.strftime('%Y-%m-06'),
            'date_to': time.strftime('%Y-%m-12'),
            'timesheet_ids': [(0, 0, line)],
        })
        sheet.signal_workflow('confirm')
        self.assertEqual(sheet.state, 'confirm')

        # fully approve timesheet
        leaves_taken_before = self.account.holiday_status_ids.sudo(
            employee.user_id
        ).leaves_taken
        sheet.sudo(manager.user_id).signal_workflow('done')
        self.assertEqual(sheet.state, 'done')

        # assert that total leave has increases
        leaves_taken_after = self.account.holiday_status_ids.sudo(
            employee.user_id
        ).leaves_taken
        self.assertAlmostEqual(
            leaves_taken_before + 6.0 / 7.0,
            leaves_taken_after,
            2
        )

        # resubmit timesheet with 8.0 hours of leave
        # sheet.create_workflow()
        # self.assertEquals(sheet.state, 'draft')
        # sheet.timesheet_ids.write(dict(unit_amount=8))
        # sheet.signal_workflow('confirm')
        # sheet.signal_workflow('done')
        # self.assertEqual(sheet.state, 'done')
        # self.assertAlmostEqual(
        #     leaves_taken_before + 8.0 / 7.0,
        #     leaves_taken_after,
        #     2
        # )
