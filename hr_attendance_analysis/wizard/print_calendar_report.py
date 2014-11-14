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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from datetime import date, time, datetime, timedelta
import math
import calendar
import pytz


class wizard_calendar_report(orm.TransientModel):

    _columns = {
        'month': fields.selection([
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ], 'Month'),
        'year': fields.integer('Year'),
        'from_date': fields.date('From date', required=True),
        'to_date': fields.date('To date', required=True),
        'employee_ids': fields.many2many(
            'hr.employee', 'calendar_report_employee_rel', 'employee_id',
            'report_id', required=True),
    }

    _defaults = {
        'month': lambda * a: str(datetime.now().month),
        'year': lambda * a: datetime.now().year,
        'from_date': lambda * a: (datetime.now() -
                                  timedelta(30)).strftime('%Y-%m-%d'),
        'to_date': lambda * a: datetime.now().strftime('%Y-%m-%d'),
        'employee_ids': (lambda self, cr, uid, context=None:
                         self.pool['hr.employee'].search(cr, uid, [],
                                                         context=None)),
    }

    _name = "attendance_analysis.wizard.calendar_report"

    def on_change_month(self, cr, uid, id_, str_month, year):
        res = {}
        if year and str_month:
            month = int(str_month)
            day = calendar.monthrange(year, month)[1]
            to_date = date(year, month, day).strftime('%Y-%m-%d')
            res = {'value': {
                'to_date': to_date,
                'from_date': date(year, month, 1).strftime('%Y-%m-%d')}}
        return res

    def print_calendar(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        attendance_obj = self.pool.get('hr.attendance')
        holidays_obj = self.pool.get('hr.holidays')
        precision = self.pool.get('res.users').browse(
            cr, uid, uid, context=context).company_id.working_time_precision
        active_tz = pytz.timezone(
            context.get("tz", "UTC") if context else "UTC")

        days_by_employee = {}

        form = self.read(cr, uid, ids, context=context)[0]
        from_date = datetime.strptime(form['from_date'], '%Y-%m-%d')
        to_date = datetime.strptime(form['to_date'], '%Y-%m-%d')
        if from_date > to_date:
            raise orm.except_orm(_('Error'), _('From date must be < to date'))
        employee_ids = form['employee_ids']
        delta = to_date - from_date
        max_number_of_attendances_per_day = 0
        active_tz = pytz.timezone(
            context.get("tz", "UTC") if context else "UTC")

        for employee_id in employee_ids:
            employee_id = str(employee_id)
            days_by_employee[employee_id] = {}
            day_count = 0
            while day_count <= delta.days:
                current_date = from_date + timedelta(day_count)
                current_total_attendances = 0.0
                current_total_overtime = 0.0
                current_total_leaves = 0.0
                # If calendar is not specified: working days = 24/7
                current_total_due = 24.0
                current_total_inside_calendar = 0.0
                str_current_date = current_date.strftime('%Y-%m-%d')
                days_by_employee[employee_id][str_current_date] = {
                    'signin_1': '',
                    'signout_1': '',
                    'signin_2': '',
                    'signout_2': '',
                    'signin_3': '',
                    'signout_3': '',
                    'signin_4': '',
                    'signout_4': '',
                }
                current_date_beginning = datetime.combine(current_date, time())
                current_date_beginning_utc = current_date_beginning.replace(
                    tzinfo=active_tz).astimezone(pytz.utc)
                str_current_date_beginning = (
                    current_date_beginning_utc.strftime('%Y-%m-%d %H:%M:%S'))
                current_date_end = datetime.combine(
                    current_date, time()) + timedelta(1)
                current_date_end_utc = current_date_end.replace(
                    tzinfo=active_tz).astimezone(pytz.utc)
                str_current_date_end = (
                    current_date_end_utc.strftime('%Y-%m-%d %H:%M:%S'))

                attendance_ids = attendance_obj.search(cr, uid, [
                    ('employee_id', '=', int(employee_id)),
                    ('name', '>=', str_current_date_beginning),
                    ('name', '<=', str_current_date_end),
                    ('action', '=', 'sign_in'),
                ], context=context)
                # computing attendance totals
                for attendance in attendance_obj.browse(
                        cr, uid, attendance_ids, context=context):
                    current_total_attendances = attendance_obj.time_sum(
                        current_total_attendances, attendance.duration)
                    current_total_overtime = attendance_obj.time_sum(
                        current_total_overtime,
                        attendance.outside_calendar_duration)
                    current_total_inside_calendar = attendance_obj.time_sum(
                        current_total_inside_calendar,
                        attendance.inside_calendar_duration)
                # printing up to 4 attendances
                if len(attendance_ids) < 5:
                    count = 1
                    for attendance in sorted(
                        attendance_obj.browse(
                            cr, uid, attendance_ids, context=context
                        ),
                        key=lambda x: x['name']
                    ):

                        attendance_start = datetime.strptime(
                            attendance.name, '%Y-%m-%d %H:%M:%S'
                            ).replace(tzinfo=pytz.utc).astimezone(active_tz)
                        attendance_end = datetime.strptime(
                            attendance.end_datetime, '%Y-%m-%d %H:%M:%S'
                            ).replace(tzinfo=pytz.utc).astimezone(active_tz)

                        days_by_employee[employee_id][str_current_date][
                            'signin_'+str(count)] = '%02d:%02d' % (
                            attendance_start.hour, attendance_start.minute)
                        days_by_employee[employee_id][str_current_date][
                            'signout_'+str(count)] = '%02d:%02d' % (
                            attendance_end.hour, attendance_end.minute)
                        count += 1
                    if len(attendance_ids) > max_number_of_attendances_per_day:
                        max_number_of_attendances_per_day = len(attendance_ids)

                days_by_employee[employee_id][str_current_date][
                    'attendances'
                ] = current_total_attendances
                days_by_employee[employee_id][str_current_date][
                    'overtime'
                ] = current_total_overtime
                reference_calendar = attendance_obj.get_reference_calendar(
                    cr, uid, int(employee_id), date=str_current_date,
                    context=context)
                # computing due total
                if reference_calendar:
                    if reference_calendar.attendance_ids:
                        current_total_due = 0.0
                        for calendar_attendance in \
                                reference_calendar.attendance_ids:
                            if (
                                (
                                    not calendar_attendance.dayofweek
                                    or
                                    int(
                                        calendar_attendance.dayofweek
                                    ) == current_date.weekday()
                                )
                                and
                                (
                                    not calendar_attendance.date_from
                                    or
                                    datetime.strptime(
                                        calendar_attendance.date_from,
                                        '%Y-%m-%d'
                                    ) <= current_date
                                )
                            ):
                                calendar_attendance_duration = (
                                    attendance_obj.time_difference(
                                        calendar_attendance.hour_from,
                                        calendar_attendance.hour_to,
                                        help_message=(
                                            'Calendar attendance ID %s'
                                            % calendar_attendance.id))
                                    )
                                if calendar_attendance_duration < 0:
                                    raise orm.except_orm(
                                        _('Error'),
                                        _("%s: 'Work to' is < 'Work from'")
                                        % calendar_attendance.name)
                                current_total_due = \
                                    attendance_obj.time_sum(
                                        current_total_due,
                                        calendar_attendance_duration)
                days_by_employee[employee_id][
                    str_current_date]['due'] = current_total_due
                # computing leaves
                holidays_ids = holidays_obj.search(cr, uid, [
                    '&', '&', '|',
                    # leave begins today
                    '&',
                    ('date_from', '>=', str_current_date_beginning),
                    ('date_from', '<=', str_current_date_end),
                    '|',
                    # leave ends today
                    '&',
                    ('date_to', '<=', str_current_date_end),
                    ('date_to', '>=', str_current_date_beginning),
                    # leave is ongoing
                    '&',
                    ('date_from', '<', str_current_date_beginning),
                    ('date_to', '>', str_current_date_end),
                    ('state', '=', 'validate'),
                    ('employee_id', '=', int(employee_id)),
                ], context=context)
                for holiday in holidays_obj.browse(
                        cr, uid, holidays_ids, context=context):
                    date_from = datetime.strptime(
                        holiday.date_from, '%Y-%m-%d %H:%M:%S')
                    date_to = datetime.strptime(
                        holiday.date_to, '%Y-%m-%d %H:%M:%S')
                    # if beginned before today
                    if date_from < current_date_beginning:
                        date_from = current_date_beginning
                    # if ends after today
                    if date_to > current_date_end:
                        date_to = current_date_end
                    date_from = date_from.replace(
                        tzinfo=pytz.utc).astimezone(active_tz)
                    date_to = date_to.replace(
                        tzinfo=pytz.utc).astimezone(active_tz)
                    duration_delta = date_to - date_from
                    duration = (
                        attendance_obj.total_seconds(duration_delta)
                        / 60.0 / 60.0
                    )
                    intervals_within = 0
                    splitted_holidays = (
                        attendance_obj.split_interval_time_by_precision(
                            date_from, duration, precision)
                    )
                    counter = 0
                    for atomic_holiday in splitted_holidays:
                        counter += 1
                        centered_holiday = (
                            attendance_obj.mid_time_interval(
                                atomic_holiday[0],
                                delta=atomic_holiday[1],
                            )
                        )
                        # check if centered_holiday is within a working
                        # schedule
                        weekday_char = str(
                            unichr(centered_holiday.weekday() + 48))
                        matched_schedule_ids = attendance_obj.matched_schedule(
                            cr, uid,
                            centered_holiday,
                            weekday_char,
                            reference_calendar.id,
                            context=context
                        )
                        if len(matched_schedule_ids) > 1:
                            raise orm.except_orm(
                                _('Error'),
                                _('Wrongly configured working schedule with '
                                  'id %s') % str(reference_calendar.id))
                        if matched_schedule_ids:
                            intervals_within += 1

                    current_total_leaves = intervals_within * precision

                days_by_employee[employee_id][str_current_date]['leaves'] = (
                    current_total_leaves)
                if current_total_leaves > days_by_employee[employee_id][
                        str_current_date]['due']:
                    days_by_employee[employee_id][str_current_date][
                        'leaves'
                    ] = days_by_employee[employee_id][str_current_date]['due']
                due_minus_leaves = attendance_obj.time_difference(
                    current_total_leaves, current_total_due,
                    help_message='Employee ID %s. Date %s' % (
                        employee_id, str_current_date))
                if due_minus_leaves < current_total_inside_calendar:
                    days_by_employee[employee_id][
                        str_current_date]['negative'] = 0.0
                else:
                    days_by_employee[employee_id][str_current_date][
                        'negative'
                        ] = attendance_obj.time_difference(
                        current_total_inside_calendar, due_minus_leaves,
                        help_message='Employee ID %s. Date %s' % (
                            employee_id, str_current_date))

                if reference_calendar:
                    if reference_calendar.leave_rounding:
                        float_rounding = float(
                            reference_calendar.leave_rounding)
                        day = days_by_employee[employee_id][str_current_date]
                        day['negative'] = math.floor(
                            day['negative'] * float_rounding) / float_rounding
                day_count += 1
        totals_by_employee = {}
        for employee_id in days_by_employee:
            totals_by_employee[employee_id] = {
                'total_attendances': 0.0,
                'total_overtime': 0.0,
                'total_negative': 0.0,
                'total_leaves': 0.0,
                'total_due': 0.0,
                'total_types': {},
            }
            for str_date in days_by_employee[employee_id]:
                totals_by_employee[employee_id]['total_attendances'] = \
                    attendance_obj.time_sum(
                        totals_by_employee[employee_id]['total_attendances'],
                        days_by_employee[employee_id][str_date]['attendances'])
                totals_by_employee[employee_id]['total_overtime'] = \
                    attendance_obj.time_sum(
                        totals_by_employee[employee_id]['total_overtime'],
                        days_by_employee[employee_id][str_date]['overtime'])
                totals_by_employee[employee_id]['total_negative'] = \
                    attendance_obj.time_sum(
                        totals_by_employee[employee_id]['total_negative'],
                        days_by_employee[employee_id][str_date]['negative'])
                totals_by_employee[employee_id]['total_leaves'] = \
                    attendance_obj.time_sum(
                        totals_by_employee[employee_id]['total_leaves'],
                        days_by_employee[employee_id][str_date]['leaves'])
                totals_by_employee[employee_id]['total_due'] = \
                    attendance_obj.time_sum(
                        totals_by_employee[employee_id]['total_due'],
                        days_by_employee[employee_id][str_date]['due'])
                # computing overtime types
                reference_calendar = attendance_obj.get_reference_calendar(
                    cr, uid, int(employee_id), date=str_date, context=context)
                if reference_calendar:
                    if reference_calendar.overtime_type_ids:
                        sorted_types = sorted(
                            reference_calendar.overtime_type_ids,
                            key=lambda k: k.sequence)
                        current_overtime = days_by_employee[employee_id][
                            str_date]['overtime']
                        for overtime_type in sorted_types:
                            emp = totals_by_employee[employee_id]
                            if not emp['total_types'].get(
                                    overtime_type.name, False):
                                emp['total_types'][overtime_type.name] = 0.0
                            if current_overtime:
                                if current_overtime <= overtime_type.limit or \
                                        not overtime_type.limit:
                                    emp['total_types'][overtime_type.name] = \
                                        attendance_obj.time_sum(
                                            emp['total_types']
                                            [overtime_type.name],
                                            current_overtime)
                                    current_overtime = 0.0
                                else:
                                    emp['total_types'][overtime_type.name] = \
                                        attendance_obj.time_sum(
                                            emp['total_types']
                                            [overtime_type.name],
                                            overtime_type.limit)
                                    current_overtime = \
                                        attendance_obj.time_difference(
                                            overtime_type.limit,
                                            current_overtime)
                days_by_employee[employee_id][str_date][
                    'attendances'
                ] = attendance_obj.float_time_convert(
                    days_by_employee[employee_id][str_date]['attendances'])
                days_by_employee[employee_id][str_date][
                    'overtime'
                ] = attendance_obj.float_time_convert(
                    days_by_employee[employee_id][str_date]['overtime'])
                days_by_employee[employee_id][str_date][
                    'negative'
                ] = attendance_obj.float_time_convert(
                    days_by_employee[employee_id][str_date]['negative'])
                days_by_employee[employee_id][str_date][
                    'leaves'
                ] = attendance_obj.float_time_convert(
                    days_by_employee[employee_id][str_date]['leaves'])
                days_by_employee[employee_id][str_date][
                    'due'
                ] = attendance_obj.float_time_convert(
                    days_by_employee[employee_id][str_date]['due'])
            totals_by_employee[employee_id][
                'total_attendances'
            ] = attendance_obj.float_time_convert(
                totals_by_employee[employee_id]['total_attendances'])
            totals_by_employee[employee_id][
                'total_overtime'
            ] = attendance_obj.float_time_convert(
                totals_by_employee[employee_id]['total_overtime'])
            totals_by_employee[employee_id][
                'total_negative'
            ] = attendance_obj.float_time_convert(
                totals_by_employee[employee_id]['total_negative'])
            totals_by_employee[employee_id][
                'total_leaves'
            ] = attendance_obj.float_time_convert(
                totals_by_employee[employee_id]['total_leaves'])
            totals_by_employee[employee_id][
                'total_due'
            ] = attendance_obj.float_time_convert(
                totals_by_employee[employee_id]['total_due'])
            for overtime_type in \
                    totals_by_employee[employee_id]['total_types']:
                totals_by_employee[employee_id]['total_types'][
                    overtime_type
                ] = attendance_obj.float_time_convert(
                    totals_by_employee[employee_id]['total_types']
                    [overtime_type])
        datas = {'ids': employee_ids}
        datas['model'] = 'hr.employee'
        datas['form'] = {}
        datas['form']['days_by_employee'] = days_by_employee
        datas['form']['totals_by_employee'] = totals_by_employee
        datas['form']['max_number_of_attendances_per_day'] = \
            max_number_of_attendances_per_day
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance_analysis.calendar_report',
            'datas': datas,
        }
