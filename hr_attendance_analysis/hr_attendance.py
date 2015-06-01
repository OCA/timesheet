# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from __future__ import division
from openerp.osv import fields, orm
from openerp.tools.translate import _
from datetime import datetime, timedelta
import math
from openerp.tools import float_compare
import pytz
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)


class ResCompany(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'working_time_precision': fields.float(
            'Working time precision',
            help='The precision used to analyse working times over working '
                 'schedule (hh:mm)', required=True)
    }

    _defaults = {
        'working_time_precision': 1.0 / 60  # hours
    }

    def update_attendance_data(self, cr, uid, ids, context=None):
        attendance_pool = self.pool.get('hr.attendance')
        att_ids = attendance_pool.search(cr, uid, [], context=context)
        attendance_pool.button_dummy(cr, uid, att_ids, context=context)
        return True


class HrAttendance(orm.Model):
    # ref: https://bugs.launchpad.net/openobject-client/+bug/887612
    # test: 0.9853 - 0.0085

    def float_time_convert(self, float_val):
        hours = math.floor(abs(float_val))
        mins = abs(float_val) - hours
        mins = round(mins * 60)
        if mins >= 60.0:
            hours = hours + 1
            mins = 0.0
        float_time = '%02d:%02d' % (hours, mins)
        return float_time

    def float_to_datetime(self, float_val):
        str_float = self.float_time_convert(float_val)
        hours = int(str_float.split(':')[0])
        minutes = int(str_float.split(':')[1])
        days = 1
        if hours / 24 > 0:
            days += hours / 24
            hours = hours % 24
        return datetime(1900, 1, int(days), hours, minutes)

    def float_to_timedelta(self, float_val):
        str_time = self.float_time_convert(float_val)
        return timedelta(0, int(str_time.split(':')[0]) * 3600.0
                         + int(str_time.split(':')[1]) * 60.0)

    def total_seconds(self, td):
        return (td.microseconds + (td.seconds + td.days * 24 * 3600)
                * 10 ** 6) / 10 ** 6

    def time_difference(
        self, float_start_time, float_end_time, help_message=False
    ):
        if float_compare(
            float_end_time, float_start_time, precision_rounding=0.0000001
        ) == -1:
            # that means a difference smaller than 0.36 milliseconds
            message = _('End time %s < start time %s %s') % (
                unicode(float_end_time),
                unicode(float_start_time),
                help_message and '(' + help_message + ')' or ''
                )
            raise orm.except_orm(
                _('Error'),
                message
            )
        delta = (self.float_to_datetime(float_end_time) -
                 self.float_to_datetime(float_start_time))
        return self.total_seconds(delta) / 3600.0

    def time_sum(self, float_first_time, float_second_time):
        str_first_time = self.float_time_convert(float_first_time)
        first_timedelta = timedelta(
            0, int(str_first_time.split(':')[0]) * 3600.0 +
            int(str_first_time.split(':')[1]) * 60.0)
        str_second_time = self.float_time_convert(float_second_time)
        second_timedelta = timedelta(
            0, int(str_second_time.split(':')[0]) * 3600.0 +
            int(str_second_time.split(':')[1]) * 60.0)
        return self.total_seconds(
            first_timedelta + second_timedelta) / 60.0 / 60.0

    def split_interval_time_by_precision(
            self, start_datetime, duration, precision=0.25
    ):
        # start_datetime: datetime, duration: hours, precision: hours
        # returns [(datetime, hours)]
        res = []
        while (duration > precision):
            res.append((start_datetime, precision))
            start_datetime += timedelta(hours=precision)
            duration -= precision
        if duration > precision / 2.0:
            res.append((start_datetime, precision))
        return res

    def datetime_to_hour(self, datetime_):
        hour = (
            datetime_.hour + datetime_.minute / 60.0
            + datetime_.second / 3600.0
        )
        return hour

    def mid_time_interval(self, datetime_start, delta):
        return datetime_start + timedelta(hours=delta / 2.0)

    def matched_schedule(
            self, cr, uid,
            datetime_, weekday_char, calendar_id,
            context=None
    ):
        calendar_attendance_pool = self.pool.get(
            'resource.calendar.attendance')
        datetime_hour = self.datetime_to_hour(datetime_)
        matched_schedule_ids = calendar_attendance_pool.search(
            cr,
            uid,
            [
                '&',
                '|',
                ('date_from', '=', False),
                ('date_from', '<=', datetime_.date()),
                '|',
                ('dayofweek', '=', False),
                ('dayofweek', '=', weekday_char),
                ('calendar_id', '=', calendar_id),
                ('hour_to', '>=', datetime_hour),
                ('hour_from', '<=', datetime_hour),
            ],
            context=context
        )
        return matched_schedule_ids

    def get_reference_calendar(
        self, cr, uid, employee_id, date=None, context=None
    ):
        if date is None:
            date = fields.date.context_today(self, cr, uid, context=context)
        contract_pool = self.pool.get('hr.contract')
        active_contract_ids = contract_pool.search(cr, uid, [
            '&',
            ('employee_id', '=', employee_id),
            '|',
            '&',
            ('date_start', '<=', date),
            '|',
            ('date_end', '>=', date),
            ('date_end', '=', False),
            '&',
            '&',
            ('trial_date_start', '!=', False),
            ('trial_date_start', '<=', date),
            '&',
            ('trial_date_end', '!=', False),
            ('trial_date_end', '>=', date),
        ], context=context)
        if len(active_contract_ids) > 1:
            lang_pool = self.pool['res.lang']
            lang_id = lang_pool.search(
                cr, uid, [('code', '=', context.get('lang'))],
                context=context
            )
            lang_data = lang_pool.read(
                cr, uid, lang_id, ['date_format'], context=context
            )
            if lang_data:
                date_format = lang_data[0]['date_format']
            else:
                date_format = DEFAULT_SERVER_DATE_FORMAT
            employee = self.pool.get('hr.employee').browse(
                cr, uid, employee_id, context=context)
            msg = _('Too many active contracts for employee %s at date %s')
            raise orm.except_orm(
                _('Error'), msg % (employee.name,
                                   datetime.strftime(date, date_format)))
        elif active_contract_ids:
            contract = contract_pool.browse(
                cr, uid, active_contract_ids[0], context=context)
            return contract.working_hours
        else:
            return orm.browse_null()

    def _ceil_rounding(self, rounding, datetime_):
        minutes = (datetime_.minute / 60.0
                   + datetime_.second / 3600.0)
        return math.ceil(minutes * rounding) / rounding

    def _floor_rounding(self, rounding, datetime_):
        minutes = (datetime_.minute / 60.0
                   + datetime_.second / 3600.0)
        return math.floor(minutes * rounding) / rounding

    def _get_attendance_duration(self, cr, uid, ids, field_name, arg,
                                 context=None):
        res = {}
        attendance_pool = self.pool['resource.calendar.attendance']
        precision = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id.working_time_precision
        # 2012.10.16 LF FIX : Get timezone from context
        active_tz = pytz.timezone(
            context.get("tz", "UTC") if context else "UTC")
        str_now = datetime.strftime(datetime.now(),
                                    DEFAULT_SERVER_DATETIME_FORMAT)
        for attendance_id in ids:
            duration = 0.0
            attendance = self.browse(cr, uid, attendance_id, context=context)
            res[attendance.id] = {}
            # 2012.10.16 LF FIX : Attendance in context timezone
            attendance_start = datetime.strptime(
                attendance.name, DEFAULT_SERVER_DATETIME_FORMAT).replace(
                tzinfo=pytz.utc).astimezone(active_tz)
            next_attendance_date = str_now
            next_attendance_ids = False
            # should we compute for sign out too?
            if attendance.action == 'sign_in':
                next_attendance_ids = self.search(
                    cr, uid, [('employee_id', '=', attendance.employee_id.id),
                              ('name', '>', attendance.name)], order='name',
                    context=context)
                if next_attendance_ids:
                    next_attendance = self.browse(
                        cr, uid, next_attendance_ids[0], context=context)
                    if next_attendance.action == 'sign_in':
                        # 2012.10.16 LF FIX : Attendance in context timezone
                        raise orm.except_orm(
                            _('Error'),
                            _('Incongruent data: sign-in %s is followed by '
                              'another sign-in') % attendance_start)
                    next_attendance_date = next_attendance.name
                # 2012.10.16 LF FIX : Attendance in context timezone
                attendance_stop = datetime.strptime(
                    next_attendance_date,
                    DEFAULT_SERVER_DATETIME_FORMAT).replace(
                    tzinfo=pytz.utc).astimezone(active_tz)
                duration_delta = attendance_stop - attendance_start
                duration = self.total_seconds(duration_delta) / 3600.0
                duration = round(duration / precision) * precision
            res[attendance.id]['duration'] = duration
            res[attendance.id]['end_datetime'] = next_attendance_date
            # If calendar is not specified: working days = 24/7
            res[attendance.id]['inside_calendar_duration'] = duration
            res[attendance.id]['outside_calendar_duration'] = 0.0
            reference_calendar = self.get_reference_calendar(
                cr, uid, attendance.employee_id.id, date=str_now[:10],
                context=context)
            if reference_calendar and next_attendance_ids:
                if reference_calendar:
                    # TODO applicare prima arrotondamento o tolleranza?
                    if reference_calendar.attendance_rounding:
                        float_attendance_rounding = float(
                            reference_calendar.attendance_rounding)
                        rounded_start_hour = self._ceil_rounding(
                            float_attendance_rounding, attendance_start)
                        rounded_stop_hour = self._floor_rounding(
                            float_attendance_rounding, attendance_stop)
                        # if shift is approximately one hour
                        if abs(1 - rounded_start_hour) < 0.01:
                            attendance_start = datetime(
                                attendance_start.year,
                                attendance_start.month,
                                attendance_start.day,
                                attendance_start.hour + 1)
                        else:
                            attendance_start = datetime(
                                attendance_start.year, attendance_start.month,
                                attendance_start.day, attendance_start.hour,
                                int(round(rounded_start_hour * 60.0)))
                        attendance_stop = datetime(
                            attendance_stop.year, attendance_stop.month,
                            attendance_stop.day, attendance_stop.hour,
                            int(round(rounded_stop_hour * 60.0)))
                        # again
                        duration_delta = attendance_stop - attendance_start
                        duration = self.total_seconds(
                            duration_delta) / 3600.0
                        duration = round(duration / precision) * precision
                        res[attendance.id]['duration'] = duration
                    res[attendance.id]['inside_calendar_duration'] = 0.0
                    res[attendance.id]['outside_calendar_duration'] = 0.0
                    calendar_id = reference_calendar.id
                    intervals_within = 0
                    # split attendance in intervals = precision
                    # 2012.10.16 LF FIX : no recursion in split attendance
                    splitted_attendances = (
                        self.split_interval_time_by_precision(
                            attendance_start, duration, precision))
                    counter = 0
                    for atomic_attendance in splitted_attendances:
                        counter += 1
                        centered_attendance = (
                            self.mid_time_interval(
                                atomic_attendance[0],
                                delta=atomic_attendance[1],
                            )
                        )
                        # check if centered_attendance is within a working
                        # schedule
                        # 2012.10.16 LF FIX : weekday must be single character
                        # not int
                        weekday_char = unicode(
                            unichr(centered_attendance.weekday() + 48))
                        matched_schedule_ids = self.matched_schedule(
                            cr, uid,
                            centered_attendance,
                            weekday_char,
                            calendar_id,
                            context=context
                        )
                        if len(matched_schedule_ids) > 1:
                            raise orm.except_orm(
                                _('Error'),
                                _('Wrongly configured working schedule with '
                                  'id %s') % unicode(calendar_id))
                        if matched_schedule_ids:
                            intervals_within += 1
                            # sign in tolerance
                            if intervals_within == 1:
                                att = attendance_pool.browse(
                                    cr, uid, matched_schedule_ids[0],
                                    context=context)
                                att_start = self.datetime_to_hour(
                                    attendance_start)
                                if (att.hour_from and
                                        (att_start >= att_start -
                                         att.hour_from - att.tolerance_to)
                                        < 0.01):
                                    # handling float roundings (<=)
                                    additional_intervals = round(
                                        (att_start - att.hour_from) /
                                        precision)
                                    intervals_within += additional_intervals
                                    res[attendance.id]['duration'] = \
                                        self.time_sum(
                                            res[attendance.id]['duration'],
                                            additional_intervals * precision)
                            # sign out tolerance
                            if len(splitted_attendances) == counter:
                                att = attendance_pool.browse(
                                    cr, uid, matched_schedule_ids[0],
                                    context=context)
                                att_stop = self.datetime_to_hour(
                                    attendance_stop)
                                if (att_stop <= att.hour_to and
                                        (att_stop -
                                         att.hour_to + att.tolerance_from) >
                                        -0.01):
                                    # handling float roundings (>=)
                                    additional_intervals = round(
                                        (att.hour_to - att_stop) /
                                        precision)
                                    intervals_within += additional_intervals
                                    res[attendance.id]['duration'] = (
                                        self.time_sum(
                                            res[attendance.id]['duration'],
                                            additional_intervals * precision)
                                    )
                    res[attendance.id][
                        'inside_calendar_duration'
                        ] = intervals_within * precision
                    # make difference using time in order to avoid
                    # rounding errors
                    # inside_calendar_duration can't be > duration
                    res[attendance.id][
                        'outside_calendar_duration'
                        ] = self.time_difference(
                        res[attendance.id]['inside_calendar_duration'],
                        res[attendance.id]['duration'],
                        help_message='Attendance ID %s' % attendance.id)

                    if reference_calendar.overtime_rounding:
                        if res[attendance.id]['outside_calendar_duration']:
                            overtime = res[attendance.id][
                                'outside_calendar_duration']
                            cal = reference_calendar
                            if cal.overtime_rounding_tolerance:
                                overtime = self.time_sum(
                                    overtime, cal.overtime_rounding_tolerance)
                            float_overtime_rounding = float(
                                reference_calendar.overtime_rounding)
                            res[attendance.id]['outside_calendar_duration'] = \
                                math.floor(overtime *
                                           float_overtime_rounding) / \
                                float_overtime_rounding
        return res

    def _get_by_contracts(self, cr, uid, ids, context=None):
        attendance_ids = []
        attendance_pool = self.pool['hr.attendance']
        for contract in self.pool['hr.contract'].browse(
                cr, uid, ids, context=context):
            att_ids = attendance_pool.search(
                cr, uid,
                [('employee_id', '=', contract.employee_id.id)],
                context=context)
            for att_id in att_ids:
                if att_id not in attendance_ids:
                    attendance_ids.append(att_id)
        return attendance_ids

    def _get_by_calendars(self, cr, uid, ids, context=None):
        attendance_ids = []
        attendance_pool = self.pool['hr.attendance']
        contract_pool = self.pool['hr.contract']
        for calendar in self.pool['resource.calendar'].browse(
                cr, uid, ids, context=context):
            contract_ids = contract_pool.search(
                cr, uid,
                [('working_hours', '=', calendar.id)],
                context=context)
            att_ids = attendance_pool._get_by_contracts(
                cr, uid, contract_ids, context=None)
            for att_id in att_ids:
                if att_id not in attendance_ids:
                    attendance_ids.append(att_id)
        return attendance_ids

    def _get_by_calendar_attendances(self, cr, uid, ids, context=None):
        attendance_ids = []
        attendance_pool = self.pool['hr.attendance']
        for calendar_attendance in \
                self.pool['resource.calendar.attendance'].browse(
                    cr, uid, ids, context=context):
            att_ids = attendance_pool._get_by_calendars(
                cr, uid, [calendar_attendance.calendar_id.id], context=None)
            for att_id in att_ids:
                if att_id not in attendance_ids:
                    attendance_ids.append(att_id)
        return attendance_ids

    def _get_attendances(self, cr, uid, ids, context=None):
        attendance_ids = []
        for attendance in self.browse(cr, uid, ids, context=context):
            if (attendance.action == 'sign_in' and
                    attendance.id not in attendance_ids):
                attendance_ids.append(attendance.id)
            elif attendance.action == 'sign_out':
                previous_attendance_ids = self.search(
                    cr, uid, [('employee_id', '=', attendance.employee_id.id),
                              ('name', '<', attendance.name),
                              ('action', '=', 'sign_in')],
                    order='name', context=context)
                if (previous_attendance_ids and
                        previous_attendance_ids[-1] not in
                        attendance_ids):
                    attendance_ids.append(previous_attendance_ids[-1])
        return attendance_ids

    _inherit = "hr.attendance"

    _store_rules = {
        'hr.attendance': (_get_attendances,
                          ['name', 'action', 'employee_id'], 20),
        'hr.contract': (_get_by_contracts,
                        ['employee_id', 'date_start', 'date_end',
                         'trial_date_start', 'trial_date_end',
                         'working_hours'], 20),
        'resource.calendar': (_get_by_calendars, ['attendance_ids'], 20),
        'resource.calendar.attendance': (
            _get_by_calendar_attendances,
            ['dayofweek', 'date_from', 'hour_from', 'hour_to', 'calendar_id'],
            20
        ),
    }

    _columns = {
        'duration': fields.function(
            _get_attendance_duration, method=True, multi='duration',
            string="Attendance duration", store=_store_rules),
        'end_datetime': fields.function(
            _get_attendance_duration, method=True, multi='duration',
            type="datetime", string="End date time", store=_store_rules),
        'outside_calendar_duration': fields.function(
            _get_attendance_duration, method=True, multi='duration',
            string="Overtime", store=_store_rules),
        'inside_calendar_duration': fields.function(
            _get_attendance_duration, method=True, multi='duration',
            string="Duration within working schedule", store=_store_rules),
    }

    def button_dummy(self, cr, uid, ids, context=None):
        for att in self.browse(cr, uid, ids, context=context):
            #  By writing the 'action' field without changing it,
            #  I'm forcing the '_get_attendance_duration' to be executed
            att.write({'action': att.action})
        return True
