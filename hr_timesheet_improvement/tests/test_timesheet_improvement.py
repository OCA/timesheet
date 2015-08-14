# -*- coding: utf-8 -*-
#
#
#    Authors: Damien Crier
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

import datetime
import time
from openerp import fields, exceptions
from openerp.tests import common


class TestImprovement(common.TransactionCase):

    def setUp(self):
        super(TestImprovement, self).setUp()
        self.timesheet_line_model = self.env['hr.analytic.timesheet']
        self.attendance_model = self.env['hr.attendance']
        self.consultant = self.env.ref('product.product_product_consultant')
        self.analytic = self.env.ref('account.analytic_administratif')
        self.expense = self.env.ref('account.a_expense')
        self.journal = self.env.ref('hr_timesheet.analytic_journal')
        self.hour = self.env.ref('product.product_uom_hour')
        self.admin_user = self.env.ref('base.user_root')
        self.user = self.admin_user.copy()
        self.user.write({'name': 'TEST hr improvement'})
        self.employee = self.env.ref('hr.employee_qdp')

        self.employee.write({'product_id': self.consultant.id,
                             'journal_id': self.journal.id,
                             'user_id': self.user.id})

        self.base_line = {
            'name': 'test',
            'date': fields.Date.today(),
            'user_id': self.user.id,
            'unit_amount': 2.,
            'product_id': self.consultant.id,
            'product_uom_id': self.hour.id,
            'account_id': self.analytic.id,
            'amount': -60.,
            'general_account_id': self.expense.id,
            'journal_id': self.journal.id,
        }

    def test_change_account_name(self):
        line = self.timesheet_line_model.create(self.base_line)
        self.assertEqual(line.account_name, self.analytic.name)
        self.analytic.write({'name': 'NEW_NAME'})
        self.assertEqual(line.account_name, self.analytic.name)

    def test_timesheet_without_existing_attendances(self):
        sheet_obj = self.env['hr_timesheet_sheet.sheet']
        sheet = sheet_obj.create({'user_id': self.user.id,
                                  'employee_id': self.employee.id,
                                  'date_from': fields.Date.today()})
        att_rs = self.attendance_model.with_context(sheet_id=sheet.id).create(
            {'action': 'sign_in',
             'employee_id': self.employee.id,
             }
            )
        att_name = fields.Datetime.from_string(att_rs.name)
        att_name = fields.Date.to_string(att_name)
        self.assertEqual(fields.Date.today(), att_name)

    def test_timesheet_with_existing_attendances(self):
        sheet_obj = self.env['hr_timesheet_sheet.sheet']
        s = sheet_obj.create({'user_id': self.user.id,
                              'employee_id': self.employee.id,
                              'date_from': time.strftime("%Y-%m-01")})
        att_rs = self.attendance_model.with_context(sheet_id=s.id).create(
            {'action': 'sign_in',
             'employee_id': self.employee.id,
             'name': time.strftime("%Y-%m-01 %H:%M:%S")
             }
            )
        old_date = (
            self.attendance_model.with_context(sheet_id=s.id)._default_date()
            )
        self.assertEqual(old_date, att_rs.name)
        new_date = (
            fields.Datetime.from_string(old_date) + datetime.timedelta(hours=1)
            )
        att_rs1 = self.attendance_model.with_context(sheet_id=s.id).create(
            {'action': 'sign_out',
             'employee_id': self.employee.id,
             'name': fields.Datetime.to_string(new_date),
             }
            )
        old_date = (
            self.attendance_model.with_context(sheet_id=s.id)._default_date()
            )
        self.assertEqual(old_date, att_rs1.name)

    def test_timesheet_without_existing_timesheet(self):
        att_rs = self.attendance_model.create(
            {'action': 'sign_in',
             'employee_id': self.employee.id,
             }
            )
        att_name = fields.Datetime.from_string(att_rs.name)
        att_name = fields.Date.to_string(att_name)
        self.assertEqual(fields.Date.today(), att_name)

    def test_timesheet_2_following_sign_in(self):
        sheet_obj = self.env['hr_timesheet_sheet.sheet']
        s = sheet_obj.create({'user_id': self.user.id,
                              'employee_id': self.employee.id,
                              'date_from': time.strftime("%Y-%m-01")})
        self.attendance_model.with_context(sheet_id=s.id).create(
            {'action': 'sign_in',
             'employee_id': self.employee.id,
             'name': time.strftime("%Y-%m-01 %H:%M:%S")
             }
            )
        old_date = (
            self.attendance_model.with_context(sheet_id=s.id)._default_date()
            )
        new_date = (
            fields.Datetime.from_string(old_date) + datetime.timedelta(hours=1)
            )
        with self.assertRaises(exceptions.ValidationError):
            self.attendance_model.with_context(sheet_id=s.id).create(
                {'action': 'sign_in',
                 'employee_id': self.employee.id,
                 'name': fields.Datetime.to_string(new_date)
                 }
                )
