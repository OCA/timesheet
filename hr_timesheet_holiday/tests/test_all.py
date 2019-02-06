# -*- coding: utf-8 -*-
# © 2016 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import time

from odoo.exceptions import UserError, ValidationError
from odoo.addons.hr_holidays.tests.common import TestHrHolidaysBase


class TimesheetHolidayTest(TestHrHolidaysBase):
    def setUp(self):
        super(TimesheetHolidayTest, self).setUp()
        self.leave = self.env['hr.holidays']
        self.project = self.env['project.project']
        self.sheet = self.env['hr_timesheet_sheet.sheet']
        self.employee = self.env.ref('hr.employee_qdp')
        self.calendar = self.env.ref('resource.timesheet_group1')
        self.employee.resource_id.calendar_id = self.calendar
        self.sl = self.env.ref('hr_holidays.holiday_status_sl')
        self.calendar_attendance_mon_morning = self.env.ref(
            "resource.calendar_attendance_mon1"
        )
        self.calendar_attendance_mon_evening = self.env.ref(
            "resource.calendar_attendance_mon2"
        )

    def _get_attendance(self, *calendar_attendances):
        all = []
        for attendance in calendar_attendances:
            all.append(attendance.hour_to - attendance.hour_from)
        return sum(all)

    def _create_timesheet(self, employee, date_from, date_to):
        vals = {
            'employee_id': employee.id,
            'date_from': date_from,
            'date_to': date_to,
            'company_id': employee.company_id.id,
            'department_id': employee.department_id.id,
        }
        return self.sheet.create(vals)

    def _init_leave_account(self):
        self.project_leave = self.project.create({
            "name": "Test Project 1",
            "allow_timesheets": True,
        })
        self.account_leave = self.project_leave.analytic_account_id
        self.account_leave.write({'is_leave_account': True})
        # Link sick leave to analytic account
        sl = self.sl
        sl.write({
            'project_id': self.project_leave.id
        })

    # Create a test customer
    def test_all(self):
        # Working day is 7 hours per day
        self.env.ref('base.main_company') \
            .timesheet_hours_per_day = 7.0
        project = self.project.create({
            "name": "Test Project 1",
            "allow_timesheets": False,
        })
        account = project.analytic_account_id
        with self.assertRaises(ValidationError):
            # Create analytic account
            account.write({'is_leave_account': True})
        project.write({'allow_timesheets': True})
        account.write({'is_leave_account': True})
        # Link sick leave to analytic account
        sl = self.sl
        sl.write({
            'project_id': project.id
        })
        # Confirm leave and check hours added to account
        hours_before = sum(account.line_ids.mapped('amount'))
        # Holidays.sudo(self.user_employee_id)
        hol_empl_grp = self.leave.sudo(self.user_hruser_id)
        leave = hol_empl_grp.create({
            'name': 'One week sick leave',
            'employee_id': self.employee_emp_id,
            'holiday_status_id': self.sl.id,
            'date_from': (datetime.today() - relativedelta(days=7)),
            'date_to': datetime.today(),
            'number_of_days_temp': 7.0,
        })
        self.assertEqual(
            leave.state, 'confirm',
            'hr_holidays: newly created leave request should be in '
            'confirm state')
        leave.sudo(self.user_hruser_id).action_approve()

        # check that the create lines are for the given employee...
        self.assertEqual(account.line_ids.mapped('user_id'),
                         leave.employee_id.user_id)

        hours_after = sum(account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_after - hours_before, 35.0)

        # Test editing of lines forbidden
        self.assertRaises(ValidationError, account.line_ids[0].write, {
            'unit_amount': 5.0
        })

        # Test force editing of lines allowed
        account.line_ids[0].with_context(force_write=True).write({
            'unit_amount': 5.0
        })
        hours_after = sum(account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_after - hours_before, 33.0)

        # Refuse leave and check hours removed from account
        leave.action_refuse()
        hours_final = sum(account.line_ids.mapped('unit_amount'))
        self.assertEqual(hours_final, hours_before)

    def test_timesheet(self):
        # Create analytic account
        project = self.project.create({
            "name": 'Personal Leaves',
            "allow_timesheets": True,
        })
        account = project.analytic_account_id
        account.write({'is_leave_account': True})
        # Link sick leave to analytic account
        sl = self.sl
        sl.write({
            'analytic_account_id': account.id
        })

        hol_empl_grp = self.leave.sudo(self.user_employee_id)
        leave = hol_empl_grp.create({
            'name': 'One week sick leave',
            'employee_id': self.employee_emp_id,
            'holiday_status_id': self.sl.id,
            'date_from': time.strftime('1900-01-06'),
            'date_to': time.strftime('1900-01-12'),
            'number_of_days_temp': 7.0,
        })
        with self.assertRaises(UserError):
            leave.action_approve()

    def test_allocation(self):
        # Create analytic account
        project = self.project.create({
            "name": 'Allocation',
            "allow_timesheets": True,
        })
        account = project.analytic_account_id
        account.write({'is_leave_account': True})
        # Link sick leave to analytic account
        sl = self.sl
        sl.write({
            'analytic_account_id': account.id
        })
        leave = self.leave.create({
            'name': 'One week sick leave',
            'holiday_status_id': self.sl.id,
            'date_from': time.strftime('%Y-%m-06'),
            'date_to': time.strftime('%Y-%m-12'),
            'number_of_days_temp': 7.0,
            'employee_id': self.employee.id,
            'type': 'add'
        })
        leave.action_approve()
        self.assertEqual(
            len(leave.analytic_line_ids), 0, 'Allocation should not have '
                                             'analytic lines')

    def test_leave_based_on_caldendar_full_day(self):
        self._init_leave_account()
        self.employee.company_id.timesheet_holiday_use_calendar = True
        self.employee.company_id.timesheet_hours_per_day = 7.0

        now = datetime.now()
        next_monday_dt = now - timedelta(days=now.weekday()) + timedelta(
            weeks=1)
        next_monday_start_dt = next_monday_dt.replace(
            hour=8, minute=0, second=0, microsecond=0)
        next_monday_end_dt = next_monday_dt.replace(
            hour=18, minute=0, second=0, microsecond=0)
        hours_before = sum(self.account_leave.line_ids.mapped('amount'))
        # we create a leave request for monday only (should be 8 working hours)
        hol_empl_grp = self.leave.sudo(self.user_hruser_id)
        leave = hol_empl_grp.create({
            'name': 'One week sick leave',
            'employee_id': self.employee.id,
            'holiday_status_id': self.sl.id,
            'date_from': next_monday_start_dt,
            'date_to': next_monday_end_dt,
        })
        leave.sudo(self.user_hruser_id).action_approve()
        hours_after = sum(self.account_leave.line_ids.mapped('unit_amount'))
        hours = self._get_attendance(
            self.calendar_attendance_mon_evening,
            self.calendar_attendance_mon_morning)
        self.assertEqual(hours_after - hours_before, hours)

    def test_leave_based_on_caldendar_part_day(self):
        self._init_leave_account()
        self.employee.company_id.timesheet_holiday_use_calendar = True
        self.employee.company_id.timesheet_hours_per_day = 7.0

        now = datetime.now()
        next_monday_dt = now - timedelta(days=now.weekday()) + timedelta(
            weeks=1)
        next_monday_start_dt = next_monday_dt.replace(
            hour=10, minute=0, second=0, microsecond=0)
        next_monday_end_dt = next_monday_dt.replace(
            hour=16, minute=0, second=0, microsecond=0)
        hours_before = sum(self.account_leave.line_ids.mapped('amount'))
        # we create a leave request for monday only (should be 8 working hours)
        hol_empl_grp = self.leave.sudo(self.user_hruser_id)
        leave = hol_empl_grp.create({
            'name': 'One week sick leave',
            'employee_id': self.employee.id,
            'holiday_status_id': self.sl.id,
            'date_from': next_monday_start_dt,
            'date_to': next_monday_end_dt,
        })
        leave.sudo(self.user_hruser_id).action_approve()
        hours_after = sum(self.account_leave.line_ids.mapped('unit_amount'))
        hours = self._get_attendance(
            self.calendar_attendance_mon_evening,
            self.calendar_attendance_mon_morning)
        # in this case, we work from 8 to 10  and 16 to 17...
        self.assertEqual(hours_after - hours_before, hours - 3)

    def test_leave_based_on_caldendar_part_time(self):
        self._init_leave_account()
        self.employee.company_id.timesheet_holiday_use_calendar = True
        self.employee.company_id.timesheet_hours_per_day = 7.0

        # we no more work on monday morning
        self.calendar_attendance_mon_morning.unlink()

        now = datetime.now()
        next_monday_dt = now - timedelta(days=now.weekday()) + timedelta(
            weeks=1)
        next_monday_start_dt = next_monday_dt.replace(
            hour=8, minute=0, second=0, microsecond=0)
        next_monday_end_dt = next_monday_dt.replace(
            hour=18, minute=0, second=0, microsecond=0)
        hours_before = sum(self.account_leave.line_ids.mapped('amount'))
        # we create a leave request for monday only (should be 8 working hours)
        hol_empl_grp = self.leave.sudo(self.user_hruser_id)
        leave = hol_empl_grp.create({
            'name': 'One week sick leave',
            'employee_id': self.employee.id,
            'holiday_status_id': self.sl.id,
            'date_from': next_monday_start_dt,
            'date_to': next_monday_end_dt,
        })
        leave.sudo(self.user_hruser_id).action_approve()
        hours_after = sum(self.account_leave.line_ids.mapped('unit_amount'))
        hours = self._get_attendance(
            self.calendar_attendance_mon_evening)
        self.assertEqual(hours_after - hours_before, hours)
