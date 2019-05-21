# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import common
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class CrmPhonecallCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(CrmPhonecallCase, cls).setUpClass()
        cls.analytic_account_1 = cls.env['account.analytic.account'].create({
            'name': 'Test Account 1',
        })
        cls.analytic_account_2 = cls.env['account.analytic.account'].create({
            'name': 'Test Account 2',
        })
        cls.project_1 = cls.env['project.project'].create({
            'name': 'Test Project 1',
            'analytic_account_id': cls.analytic_account_1.id,
        })
        cls.project_2 = cls.env['project.project'].create({
            'name': 'Test Project 2',
            'analytic_account_id': cls.analytic_account_1.id,
        })
        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Test Partner 1',
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Test Partner 2',
        })

    def _phonecall_create(self, vals):
        phonecall = self.env['crm.phonecall'].create(vals)
        return phonecall

    def _test_phonecall_timesheet_asserts(self, phonecall, timesheet):
        self.assertEqual(phonecall.date.date(), timesheet.date)
        self.assertEqual(phonecall.user_id, timesheet.user_id)
        self.assertEqual(phonecall.name, timesheet.name)
        self.assertAlmostEqual(phonecall.duration / 60.0,
                               timesheet.unit_amount, places=1)

    def test_end_call(self):
        warning_cases = (
            (False, datetime.datetime(2017, 8, 25, 12, 30)),
            (datetime.datetime(2017, 8, 25, 12, 30), False),
            (False, False)
        )
        with self.assertRaises(UserError):
            for start_dt, end_dt in warning_cases:
                self.env["crm.phonecall"]._end_call(start_dt, end_dt)
        cases = (
            (datetime.datetime(2017, 8, 21, 12, 30),
             datetime.datetime(2017, 8, 21, 12, 45), 15.0),
            (datetime.datetime(2017, 7, 1, 11),
             datetime.datetime(2017, 7, 1, 10, 55), 0.0)
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
            phonecall = self._phonecall_create({'date': date, 'name': name})
            phonecall.button_end_call()
            self.assertAlmostEqual(phonecall.duration, expected_duration,
                                   places=0)

    def test_phonecall_create_write(self):
        create_cases = (
            {'date': '2017-08-21 10:15:00',
             'duration': 15,
             'name': 'test_01',
             'project_id': self.project_1.id,
             'partner_id': self.partner_1.id,
             'user_id': self.uid},
            {'date': '2017-08-21 10:15:00',
             'duration': 30,
             'name': 'test_02',
             'project_id': self.project_1.id,
             'partner_id': self.partner_1.id,
             'user_id': self.uid}
        )
        write_cases = (
            {'date': '2017-08-20 11:20:00'},
            {'duration': 20},
            {'partner_id': self.partner_2.id},
            {'project_id': self.project_2.id},
            {'partner_id': False}
        )

        create_count = 0
        for create_vals in create_cases:
            phonecall = self._phonecall_create(create_vals)
            self._test_phonecall_timesheet_asserts(phonecall,
                                                   phonecall.timesheet_ids[0])
            for write_vals in write_cases:
                phonecall.write(write_vals)
                self._test_phonecall_timesheet_asserts(
                    phonecall, phonecall.timesheet_ids[0])
            with self.assertRaises(UserError):
                phonecall.write({'date': False})
            if create_count == 0:
                phonecall.write({'project_id': False})
                self.assertFalse(phonecall.timesheet_ids)
            else:
                phonecall.write({'duration': 0})
                self.assertFalse(phonecall.timesheet_ids)
            create_count += 1
