# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from . import base
import datetime
from openerp.exceptions import ValidationError


class CrmPhonecallCase(base.BaseCase):

    def test_end_call(self):
        warning_cases = (
            (False, datetime.datetime(2015, 8, 25, 12, 30)),
            (datetime.datetime(2015, 8, 25, 12, 30), False),
            (False, False)
        )
        with self.assertRaises(ValidationError):
            for start_dt, end_dt in warning_cases:
                self.env["crm.phonecall"]._end_call(start_dt, end_dt)
        cases = (
            (datetime.datetime(2015, 8, 21, 12, 30),
             datetime.datetime(2015, 8, 21, 12, 45), 15.0),
            (datetime.datetime(2015, 7, 1, 11),
             datetime.datetime(2015, 7, 1, 10, 55), 0.0)
        )
        for start_dt, end_dt, expected_duration in cases:
            duration = self.env["crm.phonecall"]._end_call(start_dt, end_dt)
            self.assertAlmostEqual(duration, expected_duration, places=0)

    def test_button_end_call(self):
        date_10 = datetime.datetime.now() - datetime.timedelta(minutes=10)
        date_15 = datetime.datetime.now() + datetime.timedelta(minutes=15)
        cases = (
            (date_10, 'name01', 10.0),
            (date_15, 'name02', 0.0)
        )
        for date, name, expected_duration in cases:
            phonecall = self.phonecall_create({'date': date, 'name': name})
            phonecall.button_end_call()
            self.assertAlmostEqual(phonecall.duration, expected_duration,
                                   places=0)

    def test_phonecall_create_write(self):
        create_cases = (
            {'date': '2015-08-21 10:15:00',
             'duration': 15,
             'name': 'test_01',
             'analytic_account_id': self.analytic_account.id,
             'partner_id': self.partner.id,
             'user_id': self.uid},
            {'date': '2015-08-21 10:15:00',
             'duration': 30,
             'name': 'test_02',
             'analytic_account_id': self.analytic_account.id,
             'partner_id': self.partner.id,
             'user_id': self.uid}
        )
        write_cases = (
            {'date': '2015-08-20 11:20:00'},
            {'duration': 20},
            {'partner_id': self.partner2.id},
            {'analytic_account_id': self.analytic_account2.id},
            {'duration': 0},
            {'duration': -20},
            {'partner_id': False}
        )
        for create_vals in create_cases:
            phonecall = self.phonecall_create(create_vals)
            self.check_phonecall_timesheet_asserts(
                phonecall, phonecall.timesheet_ids[0])
            for write_vals in write_cases:
                phonecall.write(write_vals)
                self.check_phonecall_timesheet_asserts(
                    phonecall, phonecall.timesheet_ids[0])
            with self.assertRaises(ValidationError):
                phonecall.write({'date': False})
            phonecall.write({'analytic_account_id': False})
            self.assertFalse(phonecall.timesheet_ids)
