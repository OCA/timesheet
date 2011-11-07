# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : JB Aubort (Camptocamp)
# Author : Guewen Baconnier (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
from datetime import datetime, timedelta


def get_number_days_between_dates(date_from, date_to):
    datetime_from = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
    datetime_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
    difference = datetime_to - datetime_from
    # return result and add a day
    return difference.days + 1


class HolidaysImport(osv.osv_memory):
    _name = 'hr.timesheet.holidays.import'
    _description = 'Wizard to import holidays in a timesheet'

    def _get_default_holidays(self, cr, uid, context=None):
        res = []
        timesheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        line_obj = self.pool.get('hr.analytic.timesheet')

        timesheet_id = context['active_id']
        timesheet = timesheet_obj.browse(cr, uid, timesheet_id, context=context)
        date_from = timesheet.date_from + ' 00:00:00'
        date_to = timesheet.date_to + ' 23:59:59'
        cr.execute("select id, date_from, date_to, name from hr_holidays where\
        (\
            ((date_from <= %s and date_to >= %s and date_to <= %s) or\
            (date_from >= %s and date_from <= %s and date_to >= %s) or\
            (date_from >= %s and date_from <= %s and date_to >= %s and date_to <= %s) or\
            (date_from <= %s and date_to >= %s)) and user_id = %s and state = 'validate'\
        )", (date_from, date_from, date_to,
            date_from, date_to, date_to,
            date_from, date_to, date_from, date_to,
            date_from, date_to, uid))
        holidays = cr.fetchall()
        if not holidays:
            raise osv.except_osv(_('Information'), _('No holidays for the current timesheet.'))

        for holiday in holidays:
            valid = True
            h_id = holiday[0]
            h_date_from = holiday[1] < timesheet.date_from \
                          and date_from or holiday[1]
            h_date_to = holiday[2] > timesheet.date_to \
                        and date_to or holiday[2]
            h_name = holiday[3]

            nb_days = get_number_days_between_dates(h_date_from, h_date_to)
            for day in range(nb_days):
                str_datetime_current = (datetime.strptime(h_date_from, '%Y-%m-%d %H:%M:%S')
                                    + timedelta(days=day)).strftime('%Y-%m-%d')
                line_ids = line_obj.search(cr, uid,
                                [('date', '=', str_datetime_current),
                                 ('name', '=', h_name),
                                 ('user_id', '=', uid)], context=context)
                if line_ids:
                    valid = False
            if not valid:
                raise osv.except_osv(_('UserError'), _('Holidays already imported.'))

            res.append(h_id)

        return res

    _columns = {
        'holidays_ids': fields.many2many('hr.holidays', 'hr_holidays_rel', 'wid', 'hid', 'Holidays', domain="[('state', '=', 'validate'),('user_id','=',uid)]"),
    }

    _defaults = {
        'holidays_ids': _get_default_holidays,
    }

    def import_holidays(self, cr, uid, ids, context):
        timesheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        employee_obj = self.pool.get('hr.employee')
        al_ts_obj = self.pool.get('hr.analytic.timesheet')
        attendance_obj = self.pool.get('hr.attendance')
        anl_account_obj = self.pool.get('account.analytic.account')

        timesheet_id = context['active_id']
        timesheet = timesheet_obj.browse(cr, uid, timesheet_id, context=context)

        employee_id = employee_obj.search(cr, uid,
            [('user_id', '=', uid)], context=context)[0]

        if timesheet.state != 'draft':
            raise osv.except_osv(_('UserError'), _('You can not modify a confirmed timesheet, please ask the manager !'))

        wizard = self.browse(cr, uid, ids, context=context)[0]

        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        hours_per_day = employee.company_id.timesheet_hours_per_day
        if not hours_per_day:
            raise osv.except_osv(_('UserError'), _('The number of hours per day is not configured on the company.'))

        if not wizard.holidays_ids:
            raise osv.except_osv(_('Information'), _('No holidays to import.'))

        errors = []
        for holiday in wizard.holidays_ids:
            if not holiday.holiday_status_id.analytic_account_id.id:
                raise osv.except_osv(_('Error !'), _("Holiday Leave Type %s has no associated analytic account !") % (holiday.holiday_status_id.name,))
            analytic_account_id = holiday.holiday_status_id.analytic_account_id.id
            anl_account = anl_account_obj.browse(cr, uid, analytic_account_id, context)

            if holiday.date_from < timesheet.date_from:
                holiday.date_from = timesheet.date_from + ' 00:00:00'
            if holiday.date_to > timesheet.date_to:
                holiday.date_to = timesheet.date_to + ' 23:59:59'

            nb_days = get_number_days_between_dates(holiday.date_from, holiday.date_to)
            for day in range(nb_days):
                dt_current = (datetime.strptime(holiday.date_from, '%Y-%m-%d %H:%M:%S')
                                    + timedelta(days=day))
                str_dt_current = dt_current.strftime('%Y-%m-%d')

                day_of_the_week = dt_current.isoweekday()

                # skip the non work days
                if day_of_the_week in (6, 7):
                    continue

                # Create timesheet lines
                existing_ts_ids = al_ts_obj.search(cr, uid,
                                [('date', '=', str_dt_current),
                                 ('name', '=', holiday.name),
                                 ('user_id', '=', uid)])
                if not existing_ts_ids:
                    unit_id = al_ts_obj._getEmployeeUnit(cr, uid, context)
                    product_id = al_ts_obj._getEmployeeProduct(cr, uid, context)
                    journal_id = al_ts_obj._getAnalyticJournal(cr, uid, context)

                    holiday_day = {
                        'name': holiday.name or _('Holidays'),
                        'date': str_dt_current,
                        'unit_amount': hours_per_day,
                        'product_uom_id': unit_id,
                        'product_id': product_id,
                        'user_id':uid,
                        'account_id': anl_account.id,
                        'to_invoice': anl_account.to_invoice.id,
                        'sheet_id': timesheet.id,
                        'journal_id':  journal_id,
                    }

                    on_change_values = al_ts_obj.\
                        on_change_unit_amount(cr, uid, False, product_id,
                                              hours_per_day, employee.company_id.id,
                                              unit=unit_id, journal_id=journal_id,
                                              context=context)
                    if on_change_values:
                        holiday_day.update(on_change_values['value'])
                        al_ts_obj.create(cr, uid, holiday_day, context)
                else:
                    errors.append('%s: There already is an analytic line.' % (str_dt_current))

                # Create attendances
                existing_attendances = \
                    attendance_obj.search(cr, uid, [('name', '=', str_dt_current),
                                                    ('employee_id', '=', employee_id)])

                if not existing_attendances:
                    # get hours and minutes (tuple) from a float time
                    hours = divmod(hours_per_day * 60, 60)

                    date_end = dt_current.replace(hour=hours[0],minute=hours[1])
                    str_date_end = date_end.strftime('%Y-%m-%d %H:%M:%S')
                    start = {
                        'name': str_dt_current,
                        'action': 'sign_in',
                        'employee_id': employee_id,
                        'sheet_id': timesheet.id,
                    }
                    end = {
                        'name': str_date_end,
                        'action': 'sign_out',
                        'employee_id': employee_id,
                        'sheet_id': timesheet.id,
                    }
                    attendance_obj.create(cr, uid, start, context)
                    attendance_obj.create(cr, uid, end, context)
                else:
                    errors.append('%s: There already is an attendance.' % (str_dt_current),)
        if errors:
            errors_str = "\n".join(errors)
            raise osv.except_osv(_('Errors'), errors_str)

        return {'type': 'ir.actions.act_window_close'}

HolidaysImport()
