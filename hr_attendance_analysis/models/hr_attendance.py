# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta
import math
import time
from openerp.tools import float_compare
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResCompany(models.Model):
    _inherit = 'res.company'

    working_time_precision = fields.Float(
        string='Working time precision',
        help='The precision used to analyse working times over working '
             'schedule (hh:mm)',
        required=True,
        default=1.0 / 60,
    )

    @api.multi
    def update_attendance_data(self):
        attendance_pool = self.env['hr.attendance']
        attendances = attendance_pool.search([])
        attendances.button_dummy()
        return True


class HrAttendance(models.Model):
    # ref: https://bugs.launchpad.net/openobject-client/+bug/887612
    # test: 0.9853 - 0.0085
    _inherit = "hr.attendance"

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
        int_hour = int(str_time.split(":")[0])
        int_minute = int(str_time.split(":")[1])
        return timedelta(
            0,
            (int_hour * 3600.0) + (int_minute * 6.0)),

    def total_seconds(self, td):
        return (td.microseconds +
                (td.seconds + td.days * 24 * 3600) * 10 ** 6) / \
            10 ** 6

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
            raise UserError(message)

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
        hour = (datetime_.hour + datetime_.minute / 60.0 +
                datetime_.second / 3600.0)
        return hour

    def mid_time_interval(self, datetime_start, delta):
        return datetime_start + timedelta(hours=delta / 2.0)

    @api.model
    def matched_schedule(
            self,
            datetime_, weekday_char, calendar_id,
            context=None):

        calendar_attendance_pool = self.env[
            'resource.calendar.attendance']
        datetime_hour = self.datetime_to_hour(datetime_)
        matched_schedules = calendar_attendance_pool.search(
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
        )
        return matched_schedules

    @api.model
    def get_reference_calendar(
            self, employee_id, date=None):

        if date is None:
            date = fields.date.context_today()

        contract_pool = self.env['hr.contract']
        employee_pool = self.env['hr.employee']

        active_contracts = contract_pool.search([
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
        ])

        if len(active_contracts) > 1:
            employee = employee_pool.browse(employee_id)
            msg = _('Too many active contracts for employee %s at date %s')
            raise UserError(msg % (employee.name, date))
        elif active_contracts:
            contract = active_contracts[0]
            return contract.working_hours
        else:
            return None

    def _ceil_rounding(self, rounding, datetime_):
        minutes = (datetime_.minute / 60.0 +
                   datetime_.second / 3600.0)
        return math.ceil(minutes * rounding) / rounding

    def _floor_rounding(self, rounding, datetime_):
        minutes = (datetime_.minute / 60.0 +
                   datetime_.second / 3600.0)
        return math.floor(minutes * rounding) / rounding

    # TODO: this is for functional field
    @api.depends(
        "triggering_attendance_id", "triggering_attendance_id.name",
        "triggering_attendance_id.action",
        "triggering_attendance_id.employee_id",
        "employee_id.contract_ids", "employee_id.contract_ids.date_start",
        "employee_id.contract_ids.date_start",
        "employee_id.contract_ids.date_end",
        "employee_id.contract_ids.trial_date_start",
        "employee_id.contract_ids.trial_date_end",
        "employee_id.contract_ids.working_hours",
        "employee_id.contract_ids.working_hours.attendance_ids",
        "employee_id.contract_ids.working_hours.attendance_ids.dayofweek",
        "employee_id.contract_ids.working_hours.attendance_ids.date_from",
        "employee_id.contract_ids.working_hours.attendance_ids.hour_from",
        "employee_id.contract_ids.working_hours.attendance_ids.hour_to",
        "employee_id.contract_ids.working_hours.attendance_ids.calendar_id"
    )
    @api.multi
    def _compute_attendance_duration(self):
        precision = self.env['res.users'].browse(
            self.env.user.id).company_id.working_time_precision

        # 2012.10.16 LF FIX : Get timezone from context
        active_tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        str_now = datetime.strftime(datetime.now(),
                                    DEFAULT_SERVER_DATETIME_FORMAT)
        for attendance in self:
            duration = 0.0
            # 2012.10.16 LF FIX : Attendance in context timezone
            attendance_start = datetime.strptime(
                attendance.name, DEFAULT_SERVER_DATETIME_FORMAT).replace(
                tzinfo=pytz.utc).astimezone(active_tz)
            next_attendance_date = str_now
            next_attendance = False
            # should we compute for sign out too?
            if attendance.action == 'sign_in':
                next_attendances = self.search(
                    [('employee_id', '=', attendance.employee_id.id),
                     ('name', '>', attendance.name)], order='name')
                if next_attendances:
                    next_attendance = next_attendances[0]
                    if next_attendance.action == 'sign_in':
                        # 2012.10.16 LF FIX : Attendance in context timezone
                        raise UserError(
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
            attendance.duration = duration
            attendance.end_datetime = next_attendance_date
            # If calendar is not specified: working days = 24/7
            attendance.inside_calendar_duration = duration
            attendance.outside_calendar_duration = 0.0
            reference_calendar = attendance.employee_id.contract_id and \
                attendance.employee_id.contract_id.working_hours or False
            # reference_calendar = self.get_reference_calendar(
            #     attendance.employee_id.id,
            #     date=str_now[:10])
            if reference_calendar and next_attendance:
                # raise UserError("weks")
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
                        attendance.duration = duration
                    attendance.inside_calendar_duration = 0.0
                    attendance.outside_calendar_duration = 0.0
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
                        matched_schedules = self.matched_schedule(
                            centered_attendance,
                            weekday_char,
                            calendar_id,
                        )
                        if len(matched_schedules) > 1:
                            raise UserError(
                                _('Wrongly configured working schedule with '
                                  'id %s') % unicode(calendar_id))
                        if matched_schedules:
                            intervals_within += 1
                            # sign in tolerance
                            if intervals_within == 1:
                                att = matched_schedules[0]
                                att_start = self.datetime_to_hour(
                                    attendance_start)
                                if (att.hour_from and
                                        (att_start >= att_start -
                                         att.hour_from - att.tolerance_to) <
                                        0.01):
                                    # handling float roundings (<=)
                                    additional_intervals = round(
                                        (att_start - att.hour_from) /
                                        precision)
                                    intervals_within += additional_intervals
                                    attendance.duration = \
                                        self.time_sum(
                                            attendance.duration,
                                            additional_intervals * precision)
                            # sign out tolerance
                            if len(splitted_attendances) == counter:
                                att = matched_schedules[0]
                                att_stop = self.datetime_to_hour(
                                    attendance_stop)
                                if (att_stop <= att.hour_to and
                                        (att_stop -
                                         att.hour_to + att.tolerance_from) >
                                        (-0.01)):
                                    # handling float roundings (>=)
                                    additional_intervals = round(
                                        (att.hour_to - att_stop) /
                                        precision)
                                    intervals_within += additional_intervals
                                    attendance.duration = (
                                        self.time_sum(
                                            attendance.duration,
                                            additional_intervals * precision)
                                    )
                    attendance.inside_calendar_duration = intervals_within * \
                        precision
                    # make difference using time in order to avoid
                    # rounding errors
                    # inside_calendar_duration can't be > duration
                    attendance.outside_calendar_duration = \
                        self.time_difference(
                            attendance.inside_calendar_duration,
                            attendance.duration,
                            help_message='Attendance ID %s' % attendance.id,
                        )
                    if reference_calendar.overtime_rounding:
                        if attendance.outside_calendar_duration:
                            overtime = attendance.outside_calendar_duration
                            cal = reference_calendar
                            if cal.overtime_rounding_tolerance:
                                overtime = self.time_sum(
                                    overtime, cal.overtime_rounding_tolerance)
                            float_overtime_rounding = float(
                                reference_calendar.overtime_rounding)
                            attendance.outside_calendar_duration = \
                                math.floor(overtime *
                                           float_overtime_rounding) / \
                                float_overtime_rounding

    @api.depends("name", "action", "employee_id")
    @api.multi
    def _compute_triggering_attendance_id(self):
        for attendance in self:
            attendance.triggering_attendance_id = False
            if attendance.action == 'sign_in':
                attendance.triggering_attendance_id = attendance.id
            elif attendance.action == 'sign_out':
                previous_attendances = self.search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('name', '<', attendance.name),
                    ('action', '=', 'sign_in')],
                    order='name')
                if previous_attendances:
                    attendance.triggering_attendance_id = \
                        previous_attendances[-1].id

    @api.depends("name")
    @api.multi
    def _compute_day(self):
        for attendance in self:
            attendance.day = time.strftime(
                '%Y-%m-%d',
                time.strptime(attendance.name, '%Y-%m-%d %H:%M:%S'))

    triggering_attendance_id = fields.Many2one(
        string="Triggering Attendance",
        comodel_name="hr.attendance",
        compute="_compute_triggering_attendance_id",
        store=True,
    )
    duration = fields.Float(
        compute='_compute_attendance_duration',
        multi='duration',
        string="Attendance duration",
        store=True,
    )
    end_datetime = fields.Datetime(
        compute='_compute_attendance_duration',
        multi='duration',
        string="End date time",
        store=True,
    )
    outside_calendar_duration = fields.Float(
        compute='_compute_attendance_duration',
        multi='duration',
        string="Overtime",
        store=True,
    )
    inside_calendar_duration = fields.Float(
        compute='_compute_attendance_duration',
        multi='duration',
        string="Duration within working schedule",
        store=True,
    )
    day = fields.Date(
        compute='_compute_day',
        string='Day',
        store=True,
        select=1,
    )

    @api.multi
    def button_dummy(self):
        for att in self:
            #  By writing the 'action' field without changing it,
            #  I'm forcing the '_compute_attendance_duration' to be executed
            att.write({'action': att.action})
