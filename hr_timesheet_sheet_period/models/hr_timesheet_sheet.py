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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _


class HrTimesheetSheet(orm.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    _columns = {
        'hr_period_id': fields.many2one(
            'hr.period', string='Period',
            readonly=True, states={
                'draft': [('readonly', False)],
                'new': [('readonly', False)]})
    }

    def onchange_pay_period(self, cr, uid, id, hr_period_id, context=None):
        if hr_period_id:
            period = self.pool['hr.period'].browse(
                cr, uid, hr_period_id, context=context)
            return {'value': {'date_from': period.date_start,
                              'date_to': period.date_stop}}
        return {}

    def _get_current_pay_period(self, cr, uid, context=None):
        period_obj = self.pool['hr.period']
        date_today = datetime.today().strftime('%Y-%m-%d')
        period_ids = period_obj.search(cr, uid,
                                       [('date_start', '<=', date_today),
                                        ('date_stop', '>=', date_today)],
                                       context=context)
        if period_ids:
            return period_ids[0]
        else:
            return False

    def _default_date_from(self, cr, uid, context=None):
        res = super(HrTimesheetSheet, self)._default_date_from(cr, uid,
                                                               context=context)
        period_id = self._get_current_pay_period(cr, uid, context=context)
        period_obj = self.pool['hr.period']
        if period_id:
            return period_obj.browse(cr, uid, period_id,
                                     context=context).date_start
        else:
            return res

    def _default_date_to(self, cr, uid, context=None):
        res = super(HrTimesheetSheet, self)._default_date_to(cr, uid,
                                                             context=context)
        period_id = self._get_current_pay_period(cr, uid, context=context)
        period_obj = self.pool['hr.period']
        if period_id:
            return period_obj.browse(cr, uid, period_id,
                                     context=context).date_stop
        else:
            return res

    def _default_hr_period_id(self, cr, uid, context=None):
        return self._get_current_pay_period(cr, uid, context=context)

    _defaults = {
        'date_from': _default_date_from,
        'date_to': _default_date_to,
        'hr_period_id': _default_hr_period_id,
    }

    def _check_start_end_dates(self, cr, uid, ids):
        for timesheet in self.browse(cr, uid, ids):
            if timesheet.hr_period_id:
                if timesheet.date_from != timesheet.hr_period_id.date_start:
                    raise orm.except_orm(
                        _('Error:'),
                        _("The Date From must match with that of the "
                          "Payslip period '%s'.") % (
                            timesheet.hr_period_id.name))
                if timesheet.date_to != timesheet.hr_period_id.date_stop:
                    raise orm.except_orm(
                        _('Error:'),
                        _("The Date To must match with that of the "
                          "Payslip period '%s'.") % (
                            timesheet.hr_period_id.name))
        return True

    _constraints = [
        (_check_start_end_dates, "Error msg in raise",
            ['date_from', 'date_to', 'hr_period_id']),
    ]
