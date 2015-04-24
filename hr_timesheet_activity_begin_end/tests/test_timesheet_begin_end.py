# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import fields, exceptions
from openerp.tests import common


class TestBeginEnd(common.TransactionCase):

    def setUp(self):
        super(TestBeginEnd, self).setUp()
        self.timesheet_line_model = self.env['hr.analytic.timesheet']
        self.consultant = self.env.ref('product.product_product_consultant')
        self.analytic = self.env.ref('account.analytic_administratif')
        self.expense = self.env.ref('account.a_expense')
        self.journal = self.env.ref('hr_timesheet.analytic_journal')
        self.hour = self.env.ref('product.product_uom_hour')
        self.user = self.env.ref('base.user_root')
        self.base_line = {
            'name': 'test',
            'date': fields.Date.today(),
            'time_start': 10.,
            'time_stop': 12.,
            'user_id': self.user.id,
            'unit_amount': 2.,
            'product_id': self.consultant.id,
            'product_uom_id': self.hour.id,
            'account_id': self.analytic.id,
            'amount': -60.,
            'general_account_id': self.expense.id,
            'journal_id': self.journal.id,
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
        message_re = (r"The beginning hour \(\d\d:\d\d\) must precede "
                      r"the ending hour \(\d\d:\d\d\)\.")
        line = self.base_line.copy()
        line.update({
            'time_start': 12.,
            'time_stop': 10.,
        })
        with self.assertRaisesRegexp(exceptions.ValidationError, message_re):
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
