# -*- coding: utf-8 -*-
# Copyright 2015 Camptocamp SA - Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, exceptions
from odoo.tests import common


class TestBeginEnd(common.TransactionCase):
    def setUp(self):
        super(TestBeginEnd, self).setUp()
        self.timesheet_line_model = self.env['account.analytic.line']
        self.analytic = self.env.ref('analytic.analytic_administratif')
        self.user = self.env.ref('base.user_root')
        self.base_line = {
            'name': 'test',
            'date': fields.Date.today(),
            'time_start': 10.,
            'time_stop': 12.,
            'user_id': self.user.id,
            'unit_amount': 2.,
            'account_id': self.analytic.id,
            'amount': -60.,
        }

    def test_onchange(self):
        line = self.timesheet_line_model.new({
            'name': 'test',
            'time_start': 10.,
            'time_stop': 12.,
        })
        line.onchange_hours_start_stop()
        self.assertEquals(line.unit_amount, 2)

    def test_check_begin_before_end(self):
        line = self.base_line.copy()
        line.update({
            'time_start': 12.,
            'time_stop': 10.,
        })
        with self.assertRaises(exceptions.ValidationError):
            self.timesheet_line_model.create(line)

    def test_check_wrong_duration(self):
        message_re = (r"The duration \(\d\d:\d\d\) must be equal to the "
                      r"difference between the hours \(\d\d:\d\d\)\.")
        line = self.base_line.copy()
        line.update({
            'time_start': 10.,
            'time_stop': 12.,
            'unit_amount': 5.,
        })
        with self.assertRaisesRegexp(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line)

    def test_check_overlap(self):
        line1 = self.base_line.copy()
        line1.update({'time_start': 10., 'time_stop': 12., 'unit_amount': 2.})
        line2 = self.base_line.copy()
        line2.update({'time_start': 12., 'time_stop': 14., 'unit_amount': 2.})
        self.timesheet_line_model.create(line1)
        self.timesheet_line_model.create(line2)

        message_re = r"overlap"

        line3 = self.base_line.copy()

        line3.update({'time_start': 9., 'time_stop': 11, 'unit_amount': 2.})
        with self.assertRaisesRegexp(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)

        line3.update({'time_start': 13., 'time_stop': 15, 'unit_amount': 2.})
        with self.assertRaisesRegexp(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)

        line3.update({'time_start': 8., 'time_stop': 15, 'unit_amount': 7.})
        with self.assertRaisesRegexp(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)
