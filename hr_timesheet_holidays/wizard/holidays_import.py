# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: JB Aubort (Camptocamp)
#    Author: Guewen Baconnier (Camptocamp)
#    Copyright 2011 Camptocamp SA
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
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)


def get_number_days_between_dates(date_from, date_to):
    datetime_from = datetime.strptime(
        date_from, DEFAULT_SERVER_DATETIME_FORMAT)
    datetime_to = datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)
    difference = datetime_to - datetime_from
    # return result and add a day
    return difference.days + 1


def get_start_of_day(date_str):
    dt_start = datetime.strptime(date_str, DEFAULT_SERVER_DATE_FORMAT)
    return dt_start.replace(hour=0, minute=0, second=0)


def get_end_of_day(date_str):
    dt_end = datetime.strptime(date_str, DEFAULT_SERVER_DATE_FORMAT)
    return dt_end.replace(hour=23, minute=59, second=59)


def get_utc_datetime(date, local_tz):
    local_dt = local_tz.localize(date)
    return local_dt.astimezone(pytz.utc)


def get_utc_start_of_day(date_str, local_tz):
    return get_utc_datetime(get_start_of_day(date_str), local_tz)


def get_utc_end_of_day(date_str, local_tz):
    return get_utc_datetime(get_end_of_day(date_str), local_tz)


class HolidaysImport(orm.TransientModel):
    _name = 'hr.timesheet.holidays.import'
    _description = 'Wizard to import holidays in a timesheet'

    def _get_default_holidays(self, cr, uid, context=None):
        res = []
        timesheet_obj = self.pool['hr_timesheet_sheet.sheet']
        line_obj = self.pool['hr.analytic.timesheet']
        timesheet_id = context['active_id']
        timesheet = timesheet_obj.browse(
            cr, uid, timesheet_id, context=context)
        local_tz = timezone(context.get('tz'))
        date_from = get_start_of_day(timesheet.date_from)
        date_from_str = date_from.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_utc_from = get_utc_datetime(date_from, local_tz).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        date_to = get_end_of_day(timesheet.date_to)
        date_to_str = date_to.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_utc_to = get_utc_datetime(date_to, local_tz).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        cr.execute("select id, date_from, date_to, name from hr_holidays where "
                   "(((date_from <= %s and date_to >= %s and date_to <= %s) or "
                   "(date_from >= %s and date_from <= %s and date_to >= %s) or "
                   "(date_from >= %s and date_from <= %s and date_to >= %s and "
                   "date_to <= %s) or "
                   "(date_from <= %s and date_to >= %s)) and user_id = %s and "
                   "state = 'validate')",
                   (date_utc_from, date_utc_from, date_utc_to,
                    date_utc_from, date_utc_to, date_utc_to,
                    date_utc_from, date_utc_to, date_utc_from, date_utc_to,
                    date_utc_from, date_utc_to, uid))
        holidays = cr.fetchall()
        if not holidays:
            raise orm.except_orm(
                _('Information'), _('No holidays for the current timesheet.'))
        for holiday in holidays:
            valid = True
            h_id = holiday[0]
            h_date_from = holiday[1] < timesheet.date_from \
                and date_from_str or holiday[1]
            h_date_to = holiday[2] > timesheet.date_to \
                and date_to_str or holiday[2]
            h_name = holiday[3]
            nb_days = get_number_days_between_dates(h_date_from, h_date_to)
            for day in range(nb_days):
                str_datetime_current = (
                    datetime.strptime(h_date_from,
                                      DEFAULT_SERVER_DATETIME_FORMAT)
                    + timedelta(days=day)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                line_ids = line_obj.search(
                    cr, uid, [('date', '=', str_datetime_current),
                              ('name', '=', h_name),
                              ('user_id', '=', uid)], context=context)
                if line_ids:
                    valid = False
            if not valid:
                raise orm.except_orm(
                    _('UserError'), _('Holidays already imported.'))
            res.append(h_id)
        return res

    _columns = {
        'holidays_ids': fields.many2many(
            'hr.holidays', 'hr_holidays_rel', 'id', 'holiday_id', 'Holidays',
            domain="[('state', '=', 'validate'),('user_id','=',uid)]"),
    }

    _defaults = {
        'holidays_ids': _get_default_holidays,
    }

    def import_holidays(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        timesheet_obj = self.pool['hr_timesheet_sheet.sheet']
        employee_obj = self.pool['hr.employee']
        al_ts_obj = self.pool['hr.analytic.timesheet']
        attendance_obj = self.pool['hr.attendance']
        anl_account_obj = self.pool['account.analytic.account']
        timesheet_id = context['active_id']
        timesheet = timesheet_obj.browse(cr, uid, timesheet_id, context=context)
        employee_id = employee_obj.search(
            cr, uid, [('user_id', '=', uid)], context=context)[0]
        if timesheet.state != 'draft':
            raise orm.except_orm(
                _('UserError'),
                _('You can not modify a confirmed timesheet, please ask the '
                  'manager !'))
        wizard = self.browse(cr, uid, ids, context=context)[0]
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        hours_per_day = employee.company_id.timesheet_hours_per_day
        if not hours_per_day:
            raise orm.except_orm(
                _('UserError'),
                _('The number of hours per day is not configured on the '
                  'company.'))
        if not wizard.holidays_ids:
            raise orm.except_orm(_('Information'), _('No holidays to import.'))
        local_tz = timezone(context.get('tz'))
        errors = []
        for holiday in wizard.holidays_ids:
            if not holiday.holiday_status_id.analytic_account_id.id:
                raise orm.except_orm(
                    _('Error !'),
                    _("Holiday Leave Type %s has no associated analytic "
                      "account !") % holiday.holiday_status_id.name)
            analytic_account_id = \
                holiday.holiday_status_id.analytic_account_id.id
            anl_account = anl_account_obj.browse(cr, uid, analytic_account_id,
                                                 context)
            if holiday.date_from < timesheet.date_from:
                dt_ts_from = get_utc_start_of_day(timesheet.date_from, local_tz)
                holiday.date_from = dt_ts_from.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
            if holiday.date_to > timesheet.date_to:
                dt_ts_to = get_utc_end_of_day(timesheet.date_to, local_tz)
                holiday.date_to = dt_ts_to.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
            nb_days = get_number_days_between_dates(holiday.date_from,
                                                    holiday.date_to)
            for day in range(nb_days):
                dt_current = (datetime.strptime(holiday.date_from,
                                                DEFAULT_SERVER_DATETIME_FORMAT)
                              + timedelta(days=day))
                # datetime as date at midnight
                str_dt_current = dt_current.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
                dt_utc_current = get_utc_datetime(
                    dt_current.replace(hour=0, minute=0, second=0), local_tz)
                str_dt_utc_current = dt_utc_current.strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT)
                # Test if is week day in local tz
                day_of_the_week = dt_current.isoweekday()
                # skip the non work days
                if day_of_the_week in (6, 7):
                    continue
                # Create timesheet lines
                existing_ts_ids = al_ts_obj.search(
                    cr, uid, [('date', '=', str_dt_current),
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
                        'user_id': uid,
                        'account_id': anl_account.id,
                        'to_invoice': anl_account.to_invoice.id,
                        'sheet_id': timesheet.id,
                        'journal_id': journal_id,
                    }
                    on_change_values = al_ts_obj.on_change_unit_amount(
                        cr, uid, False, product_id, hours_per_day,
                        employee.company_id.id, unit=unit_id,
                        journal_id=journal_id, context=context)
                    if on_change_values:
                        holiday_day.update(on_change_values['value'])
                        al_ts_obj.create(cr, uid, holiday_day, context)
                else:
                    errors.append('%s: There already is an analytic line.' %
                                  str_dt_current)
                # Create attendances
                existing_attendances = attendance_obj.search(
                    cr, uid, [('name', '=', str_dt_utc_current),
                              ('employee_id', '=', employee_id)])
                if not existing_attendances:
                    # get hours and minutes (tuple) from a float time
                    hours = divmod(hours_per_day * 60, 60)
                    date_end = dt_utc_current + \
                        timedelta(hours=int(hours[0]), minutes=int(hours[1]))
                    str_date_end = date_end.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)
                    start = {
                        'name': str_dt_utc_current,
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
                    errors.append('%s: There already is an attendance.' %
                                  str_dt_current)
        if errors:
            errors_str = "\n".join(errors)
            raise orm.except_orm(_('Errors'), errors_str)
        return {'type': 'ir.actions.act_window_close'}
