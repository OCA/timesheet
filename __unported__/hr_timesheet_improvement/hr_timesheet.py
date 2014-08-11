# -*- coding: utf-8 -*-
##############################################################################
#
#    Author : Yannick Vaucher (Camptocamp)
#    Copyright 2013 Camptocamp SA
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
from openerp.osv import orm, fields


class HrAnalyticTimesheet(orm.Model):
    """Set order by line date and analytic account name instead of id
    We create related stored values as _order cannot be used on inherited
    columns.
    """
    _inherit = "hr.analytic.timesheet"
    _order = "date_aal DESC, account_name ASC"

    def _get_account_analytic_line(self, cr, uid, ids, context=None):
        ts_line_ids = self.pool.get('hr.analytic.timesheet').search(
            cr, uid, [('line_id', 'in', ids)])
        return ts_line_ids

    def _get_account_analytic_account(self, cr, uid, ids, context=None):
        ts_line_ids = self.pool.get('hr.analytic.timesheet').search(
            cr, uid, [('account_id', 'in', ids)])
        return ts_line_ids

    _columns = {
        'date_aal': fields.related(
            'line_id', 'date', string="Analytic Line Date", type='date',
            store={
                'account.analytic.line': (_get_account_analytic_line, ['date'],
                                          10),
                'hr.analytic.timesheet': (lambda self, cr, uid, ids,
                                          context=None: ids, None, 10)}),
        'account_name': fields.related(
            'account_id', 'name', string="Analytic Account Name", type='char',
            size=256,
            store={
                'account.analytic.account': (_get_account_analytic_account,
                                             ['name'], 10),
                'hr.analytic.timesheet': (lambda self, cr, uid, ids,
                                          context=None: ids, None, 10)}),
    }
