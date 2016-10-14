# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import orm


class hr_timesheet_sheet(orm.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    def set_previous_timesheet_ids(self, cr, uid, ids, context=None):

        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        timesheet_obj = self.pool.get('hr.analytic.timesheet')

        for sheet in sheet_obj.browse(cr, uid, ids, context=context):
            date_from = datetime.strptime(sheet.date_from, '%Y-%m-%d')
            user = self.pool.get('res.users').browse(cr, uid, uid,
                                                     context=context)
            r = user.company_id and user.company_id.timesheet_range or 'month'
            delta = relativedelta(months=-1)
            if r == 'month':
                delta = relativedelta(months=-1)
            elif r == 'week':
                delta = relativedelta(weeks=-1)
            elif r == 'year':
                delta = relativedelta(years=-1)
            date_from_lw = (date_from + delta).strftime('%Y-%m-%d')
            emp_id = sheet.employee_id and sheet.employee_id.id or False
            if not emp_id:
                return False
            ga_id = sheet.employee_id.product_id.\
                property_account_expense.id
            if not ga_id:
                ga_id = sheet.employee_id.product_id.\
                    categ_id.property_account_expense_categ.id

            lw_sheet_ids = sheet_obj.search(
                cr, uid, [('date_to', '>=', date_from_lw),
                          ('date_from', '<=', date_from_lw),
                          ('employee_id', '=', emp_id)],
                context=context)
            a_line_ids = []
            for lw_sheet in sheet_obj.browse(cr, uid, lw_sheet_ids,
                                             context=context):
                for timesheet_id in lw_sheet.timesheet_ids:
                    if timesheet_id.line_id:
                        a_line_ids.append(timesheet_id.line_id.id)
            if a_line_ids:
                cr.execute('SELECT DISTINCT account_id '
                           'FROM account_analytic_line AS L '
                           'WHERE L.id IN %s '
                           'GROUP BY account_id', (tuple(a_line_ids),))
                res = cr.dictfetchall()
                timesheet_ids = []
                for res_vals in res:
                    same_account_id = False
                    for timesheet_id in sheet.timesheet_ids:
                        if (
                            timesheet_id.line_id
                            and timesheet_id.line_id.account_id
                            and timesheet_id.line_id.account_id.id
                            == res_vals['account_id']
                        ):
                            same_account_id = True
                    if same_account_id is True:
                        continue
                    vals = {
                        'employee_id': sheet.employee_id.id,
                        'journal_id': sheet.employee_id.journal_id.id,
                        'date': sheet.date_from,
                        'account_id': res_vals['account_id'],
                        'name': '/',
                        'product_id': sheet.employee_id.product_id.id,
                        'product_uom_id':
                            sheet.employee_id.product_id.uom_id.id,
                        'general_account_id': ga_id,
                        'user_id': context.get('user_id') or uid,
                    }

                    ts_id = timesheet_obj.create(cr, uid, vals,
                                                 context=context)
                    timesheet_ids.append(ts_id)

                if timesheet_ids:
                    sheet_obj.write(cr, uid, sheet.id,
                                    {'timesheet_ids': [(4, timesheet_id)
                                                       for timesheet_id
                                                       in timesheet_ids]})

        return False
