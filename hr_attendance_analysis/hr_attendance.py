# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time
from datetime import *
import math

import pytz

class res_company(osv.osv):

    _inherit = 'res.company'

    _columns = {
        'working_time_precision': fields.float('Working time precision', help='The precision used to analyse working times over working schedule', required=True)
        }

    _defaults = {
        'working_time_precision': 0.016666667
        }

res_company()

class hr_attendance(osv.osv):

    # ref: https://bugs.launchpad.net/openobject-client/+bug/887612
    # test: 0.9853 - 0.0085
    def float_time_convert(self, float_val):
        hours = math.floor(abs(float_val))
        mins = abs(float_val) - hours
        mins = round(mins * 60)
        if mins >= 60.0:
            hours = hours + 1
            mins = 0.0
        float_time = '%02d:%02d' % (hours,mins)
        return float_time

    def float_to_datetime(self, float_val):
        str_float = self.float_time_convert(float_val)
        hours = int(str_float.split(':')[0])
        minutes = int(str_float.split(':')[1])
        days = 1
        if hours / 24 > 0:
            days += hours / 24
            hours = hours % 24
        return datetime(1900, 1, days, hours, minutes)

    def float_to_timedelta(self, float_val):
        str_time = self.float_time_convert(float_val)
        return timedelta(0, int(str_time.split(':')[0]) * 60.0*60.0 + int(str_time.split(':')[1]) * 60.0)

    def time_difference(self, float_start_time, float_end_time):
        if float_end_time < float_start_time:
            raise osv.except_osv(_('Error'), _('End time %s < start time %s')
                % (str(float_end_time),str(float_start_time)))
        delta = self.float_to_datetime(float_end_time) - self.float_to_datetime(float_start_time)
        return delta.total_seconds() / 60.0 / 60.0

    def time_sum(self, float_first_time, float_second_time):
        str_first_time = self.float_time_convert(float_first_time)
        first_timedelta = timedelta(0, int(str_first_time.split(':')[0]) * 60.0*60.0 +
            int(str_first_time.split(':')[1]) * 60.0)
        str_second_time = self.float_time_convert(float_second_time)
        second_timedelta = timedelta(0, int(str_second_time.split(':')[0]) * 60.0*60.0 +
            int(str_second_time.split(':')[1]) * 60.0)
        return (first_timedelta + second_timedelta).total_seconds() / 60.0 / 60.0

    def _split_long_attendances(self, start_datetime, duration):
        # start_datetime: datetime, duration: hours
        # returns [(datetime, hours)]
        res = []
        if duration > 24:
            res.append((start_datetime, 24))
            res.extend(self._split_long_attendances(start_datetime + timedelta(1), duration - 24))
        else:
            res.append((start_datetime, duration))
        return res
    
    def _split_norecurse_attendance(self, start_datetime, duration, precision=025):
        # start_datetime: datetime, duration: hours, precision: hours
        # returns [(datetime, hours)]
        res = []
        while (duration > precision):
            res.append((start_datetime, precision))
            start_datetime += timedelta(0,0,0,0,0,precision)
            duration -= precision
        if duration > precision / 2.0:
            res.append((start_datetime, precision))
        return res        

    def _split_attendance(self, start_datetime, duration, precision=0.25):
        # start_datetime: datetime, duration: hours, precision: hours
        # returns [(datetime, hours)]
        res = []
        if duration > precision:
            res.append((start_datetime, precision))
            res.extend(self._split_attendance(start_datetime + timedelta(0,0,0,0,0,precision), duration - precision, precision))
        elif duration > precision / 2.0:
            res.append((start_datetime, precision))
        return res   
        
    def get_active_contracts(self, cr, uid, employee_id, date=datetime.now().strftime('%Y-%m-%d')):
        contract_pool = self.pool.get('hr.contract')
        active_contract_ids= contract_pool.search(cr, uid, [
            '&',
            ('employee_id', '=', employee_id),
            '|',
            '&',
            ('date_start', '<=', date),
            '|',
            ('date_end', '>=', date),
            ('date_end', '=', False),
            '&',
            '|',
            ('trial_date_start', '=', False),
            ('trial_date_start', '<=', date),
            '|',
            ('trial_date_end', '=', False),
            ('trial_date_end', '>=', date),
            ])
        if len(active_contract_ids) > 1:
            raise osv.except_osv(_('Error'), _('Too many active contracts for employee %s') % attendance.employee_id.name)
        return active_contract_ids

    def _ceil_rounding(self, rounding, datetime):
        minutes = datetime.minute / 60.0 \
            + datetime.second / 60.0 / 60.0
        return math.ceil(minutes * rounding) / rounding

    def _floor_rounding(self, rounding, datetime):
        minutes = datetime.minute / 60.0 \
            + datetime.second / 60.0 / 60.0
        return math.floor(minutes * rounding) / rounding

    def _get_attendance_duration(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        contract_pool = self.pool.get('hr.contract')
        resource_pool = self.pool.get('resource.resource')
        attendance_pool = self.pool.get('resource.calendar.attendance')
        precision = self.pool.get('res.users').browse(cr, uid, uid).company_id.working_time_precision
        # 2012.10.16 LF FIX : Get timezone from context
        active_tz = pytz.timezone(context.get("tz","UTC") if context else "UTC")
        str_now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        for attendance_id in ids:
            duration = 0.0
            outside_calendar_duration = 0.0
            inside_calendar_duration = 0.0
            attendance = self.browse(cr, uid, attendance_id)
            res[attendance.id] = {}
            # 2012.10.16 LF FIX : Attendance in context timezone
            attendance_start = datetime.strptime(attendance.name, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(active_tz)
            next_attendance_date = str_now
            # should we compute for sign out too?
            if attendance.action == 'sign_in':
                next_attendance_ids = self.search(cr, uid, [
                    ('employee_id', '=', attendance.employee_id.id),
                    ('name', '>', attendance.name)], order='name')
                if next_attendance_ids:
                    next_attendance = self.browse(cr, uid, next_attendance_ids[0])
                    if next_attendance.action == 'sign_in':
                         # 2012.10.16 LF FIX : Attendance in context timezone
                         raise osv.except_osv(_('Error'), _('Incongruent data: sign-in %s is followed by another sign-in') % attendance_start)
                    next_attendance_date = next_attendance.name
                # 2012.10.16 LF FIX : Attendance in context timezone
                attendance_stop = datetime.strptime(next_attendance_date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(active_tz)
                duration_delta = attendance_stop - attendance_start
                duration = duration_delta.total_seconds() / 60.0 / 60.0
                duration = round(duration / precision) * precision
            res[attendance.id]['duration'] = duration
            res[attendance.id]['end_datetime'] = next_attendance_date
            # If contract is not specified: working days = 24/7
            res[attendance.id]['inside_calendar_duration'] = duration
            res[attendance.id]['outside_calendar_duration'] = 0.0

            active_contract_ids = self.get_active_contracts(cr, uid, attendance.employee_id.id, date=str_now[:10])

            if active_contract_ids:
                contract = contract_pool.browse(cr, uid, active_contract_ids[0])
                if contract.working_hours:
                    # TODO applicare prima arrotondamento o tolleranza?
                    if contract.working_hours.attendance_rounding:
                        float_attendance_rounding = float(contract.working_hours.attendance_rounding)
                        rounded_start_hour = self._ceil_rounding(float_attendance_rounding, attendance_start)
                        rounded_stop_hour = self._floor_rounding(float_attendance_rounding, attendance_stop)
                            
                        if abs(1- rounded_start_hour) < 0.01: # if shift == 1 hour
                            attendance_start = datetime(attendance_start.year, attendance_start.month,
                                attendance_start.day, attendance_start.hour + 1)
                        else:
                            attendance_start = datetime(attendance_start.year, attendance_start.month,
                                attendance_start.day, attendance_start.hour, int(round(rounded_start_hour * 60.0)))
                                
                        attendance_stop = datetime(attendance_stop.year, attendance_stop.month,
                            attendance_stop.day, attendance_stop.hour, int(round(rounded_stop_hour * 60.0)))
                        
                        # again
                        duration_delta = attendance_stop - attendance_start
                        duration = duration_delta.total_seconds() / 60.0 / 60.0
                        duration = round(duration / precision) * precision
                        res[attendance.id]['duration'] = duration
                        
                    res[attendance.id]['inside_calendar_duration'] = 0.0
                    res[attendance.id]['outside_calendar_duration'] = 0.0
                    calendar_id = contract.working_hours.id
                    intervals_within = 0

                    # split attendance in intervals = precision
                    # 2012.10.16 LF FIX : no recursion in split attendance
                    splitted_attendances = self._split_norecurse_attendance(attendance_start, duration, precision)
                    counter = 0
                    for atomic_attendance in splitted_attendances:
                        counter += 1
                        centered_attendance = atomic_attendance[0] + timedelta(0,0,0,0,0, atomic_attendance[1] / 2.0)
                        centered_attendance_hour = centered_attendance.hour + centered_attendance.minute / 60.0 \
                            + centered_attendance.second / 60.0 / 60.0
                        # check if centered_attendance is within a working schedule                        
                        # 2012.10.16 LF FIX : weekday must be single character not int
                        weekday_char = str(unichr(centered_attendance.weekday() + 48))
                        matched_schedule_ids = attendance_pool.search(cr, uid, [
                            '&',
                            '|',
                            ('date_from', '=', False),
                            ('date_from','<=',centered_attendance.date()),
                            '|',
                            ('dayofweek', '=', False),
                            ('dayofweek','=',weekday_char),
                            ('calendar_id','=',calendar_id),
                            ('hour_to','>=',centered_attendance_hour),
                            ('hour_from','<=',centered_attendance_hour),
                            ])
                        if len(matched_schedule_ids) > 1:
                            raise osv.except_osv(_('Error'),
                                _('Wrongly configured working schedule with id %s') % str(calendar_id))
                        if matched_schedule_ids:
                            intervals_within += 1
                            # sign in tolerance
                            if intervals_within == 1:
                                calendar_attendance = attendance_pool.browse(cr, uid, matched_schedule_ids[0])
                                attendance_start_hour = attendance_start.hour + attendance_start.minute / 60.0 \
                                    + attendance_start.second / 60.0 / 60.0
                                if attendance_start_hour >= calendar_attendance.hour_from and \
                                    (attendance_start_hour - (calendar_attendance.hour_from +
                                    calendar_attendance.tolerance_to)) < 0.01: # handling float roundings (<=)
                                    additional_intervals = round(
                                        (attendance_start_hour - calendar_attendance.hour_from) / precision)
                                    intervals_within += additional_intervals
                                    res[attendance.id]['duration'] = self.time_sum(
                                        res[attendance.id]['duration'], additional_intervals * precision)
                            # sign out tolerance
                            if len(splitted_attendances) == counter:
                                attendance_stop_hour = attendance_stop.hour + attendance_stop.minute / 60.0 \
                                    + attendance_stop.second / 60.0 / 60.0
                                calendar_attendance = attendance_pool.browse(cr, uid, matched_schedule_ids[0])
                                if attendance_stop_hour <= calendar_attendance.hour_to and \
                                    (attendance_stop_hour - (calendar_attendance.hour_to -
                                    calendar_attendance.tolerance_from)) > -0.01: # handling float roundings (>=)
                                    additional_intervals = round(
                                        (calendar_attendance.hour_to - attendance_stop_hour) / precision)
                                    intervals_within += additional_intervals
                                    res[attendance.id]['duration'] = self.time_sum(
                                        res[attendance.id]['duration'], additional_intervals * precision)

                    res[attendance.id]['inside_calendar_duration'] = intervals_within * precision
                    # make difference using time in order to avoid rounding errors
                    # inside_calendar_duration can't be > duration
                    res[attendance.id]['outside_calendar_duration'] = self.time_difference(
                        res[attendance.id]['inside_calendar_duration'], res[attendance.id]['duration'])

                    if contract.working_hours.overtime_rounding:
                        if res[attendance.id]['outside_calendar_duration']:
                            overtime = res[attendance.id]['outside_calendar_duration']
                            if contract.working_hours.overtime_rounding_tolerance:
                                overtime = self.time_sum(overtime,
                                    contract.working_hours.overtime_rounding_tolerance)
                            float_overtime_rounding = float(contract.working_hours.overtime_rounding)
                            res[attendance.id]['outside_calendar_duration'] = math.floor(
                                overtime * float_overtime_rounding) / float_overtime_rounding

        return res

    def _get_by_contracts(self, cr, uid, ids, context=None):
        attendance_ids = []
        attendance_pool = self.pool.get('hr.attendance')
        for contract in self.pool.get('hr.contract').browse(cr, uid, ids, context=context):
            att_ids = attendance_pool.search(cr, uid, [('employee_id', '=', contract.employee_id.id)])
            for att_id in att_ids:
                if att_id not in attendance_ids:
                    attendance_ids.append(att_id)
        return attendance_ids

    def _get_by_calendars(self, cr, uid, ids, context=None):
        attendance_ids = []
        attendance_pool = self.pool.get('hr.attendance')
        contract_pool = self.pool.get('hr.contract')
        for calendar in self.pool.get('resource.calendar').browse(cr, uid, ids, context=context):
            contract_ids = contract_pool.search(cr, uid, [('working_hours', '=', calendar.id)])
            att_ids = attendance_pool._get_by_contracts(cr, uid, contract_ids, context=None)
            for att_id in att_ids:
                if att_id not in attendance_ids:
                    attendance_ids.append(att_id)                
        return attendance_ids

    def _get_by_calendar_attendances(self, cr, uid, ids, context=None):
        attendance_ids = []
        attendance_pool = self.pool.get('hr.attendance')
        for calendar_attendance in self.pool.get('resource.calendar.attendance').browse(cr, uid, ids, context=context):
            att_ids = attendance_pool._get_by_calendars(cr, uid, [calendar_attendance.calendar_id.id], context=None)
            for att_id in att_ids:
                if att_id not in attendance_ids:
                    attendance_ids.append(att_id)
        return attendance_ids

    def _get_attendances(self, cr, uid, ids, context=None):
        attendance_ids = []
        for attendance in self.browse(cr, uid, ids, context=context):
            if attendance.action == 'sign_in' and attendance.id not in attendance_ids:
                attendance_ids.append(attendance.id)
            elif attendance.action == 'sign_out':
                previous_attendance_ids = self.search(cr, uid, [
                    ('employee_id', '=', attendance.employee_id.id),
                    ('name', '<', attendance.name)], order='name')
                if previous_attendance_ids and previous_attendance_ids[len(previous_attendance_ids) - 1] not in attendance_ids:
                    attendance_ids.append(previous_attendance_ids[len(previous_attendance_ids) - 1])    
        return attendance_ids

    _inherit = "hr.attendance"

    _columns = {
        'duration': fields.function(_get_attendance_duration, method=True, multi='duration', string="Attendance duration",
            store={
                'hr.attendance': (_get_attendances, ['name', 'action', 'employee_id'], 20),
                'hr.contract': (_get_by_contracts, ['employee_id', 'date_start', 'date_end', 'trial_date_start', 'trial_date_end', 'working_hours'], 20),
                'resource.calendar': (_get_by_calendars, ['attendance_ids'], 20),
                'resource.calendar.attendance': (_get_by_calendar_attendances, ['dayofweek', 'date_from', 'hour_from', 'hour_to', 'calendar_id'], 20),
                }
            ),
        'end_datetime': fields.function(_get_attendance_duration, method=True, multi='duration', type="datetime", string="End date time",
            store={
                'hr.attendance': (_get_attendances, ['name', 'action', 'employee_id'], 20),
                'hr.contract': (_get_by_contracts, ['employee_id', 'date_start', 'date_end', 'trial_date_start', 'trial_date_end', 'working_hours'], 20),
                'resource.calendar': (_get_by_calendars, ['attendance_ids'], 20),
                'resource.calendar.attendance': (_get_by_calendar_attendances, ['dayofweek', 'date_from', 'hour_from', 'hour_to', 'calendar_id'], 20),
                }),
        'outside_calendar_duration': fields.function(_get_attendance_duration, method=True, multi='duration',
            string="Overtime",
            store={
                'hr.attendance': (_get_attendances, ['name', 'action', 'employee_id'], 20),
                'hr.contract': (_get_by_contracts, ['employee_id', 'date_start', 'date_end', 'trial_date_start', 'trial_date_end', 'working_hours'], 20),
                'resource.calendar': (_get_by_calendars, ['attendance_ids'], 20),
                'resource.calendar.attendance': (_get_by_calendar_attendances, ['dayofweek', 'date_from', 'hour_from', 'hour_to', 'calendar_id'], 20),
                }),
        'inside_calendar_duration': fields.function(_get_attendance_duration, method=True, multi='duration',
            string="Duration within working schedule",
            store={
                'hr.attendance': (_get_attendances, ['name', 'action', 'employee_id'], 20),
                'hr.contract': (_get_by_contracts, ['employee_id', 'date_start', 'date_end', 'trial_date_start', 'trial_date_end', 'working_hours'], 20),
                'resource.calendar': (_get_by_calendars, ['attendance_ids'], 20),
                'resource.calendar.attendance': (_get_by_calendar_attendances, ['dayofweek', 'date_from', 'hour_from', 'hour_to', 'calendar_id'], 20),
                }),
    }

hr_attendance()

