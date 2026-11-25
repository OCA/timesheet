# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProjectTimesheetHolidaysBeginEnd(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        # Monday and Tuesday, in CEST (UTC+2): 08:00 local is 06:00 UTC.
        cls.monday = date(2026, 10, 5)
        cls.tuesday = date(2026, 10, 6)
        attendances = []
        for weekday in range(5):
            attendances += [
                Command.create(
                    {
                        "name": "Morning",
                        "dayofweek": str(weekday),
                        "hour_from": 8.0,
                        "hour_to": 12.0,
                        "day_period": "morning",
                    }
                ),
                Command.create(
                    {
                        "name": "Lunch",
                        "dayofweek": str(weekday),
                        "hour_from": 12.0,
                        "hour_to": 13.0,
                        "day_period": "lunch",
                    }
                ),
                Command.create(
                    {
                        "name": "Afternoon",
                        "dayofweek": str(weekday),
                        "hour_from": 13.0,
                        "hour_to": 17.0,
                        "day_period": "afternoon",
                    }
                ),
            ]
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "Split 40h",
                "tz": "Europe/Brussels",
                "hours_per_day": 8.0,
                "attendance_ids": attendances,
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "Timesheet Employee",
                "login": "timesheet_employee_begin_end",
                "tz": "Europe/Brussels",
                "group_ids": [
                    Command.set(
                        [cls.env.ref("hr_timesheet.group_hr_timesheet_user").id]
                    )
                ],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Timesheet Employee",
                "user_id": cls.user.id,
                "company_id": cls.company.id,
                "tz": "Europe/Brussels",
                "resource_calendar_id": cls.calendar.id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Internal",
                "company_id": cls.company.id,
                "allow_timesheets": True,
            }
        )
        cls.task = cls.env["project.task"].create(
            {"name": "Time Off", "project_id": cls.project.id}
        )
        cls.company.write(
            {
                "internal_project_id": cls.project.id,
                "leave_timesheet_task_id": cls.task.id,
            }
        )
        cls.leave_type_day = cls.env["hr.leave.type"].create(
            {
                "name": "Days",
                "requires_allocation": False,
                "leave_validation_type": "hr",
                "request_unit": "day",
            }
        )
        cls.leave_type_half_day = cls.leave_type_day.copy(
            {"name": "Half days", "request_unit": "half_day"}
        )
        cls.leave_type_hour = cls.leave_type_day.copy(
            {"name": "Hours", "request_unit": "hour"}
        )

    def _validate_leave(self, leave_type, date_from, date_to, env=None, **extra):
        leave = (env or self.env)["hr.leave"].create(
            {
                "name": "Holidays",
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "request_date_from": date_from,
                "request_date_to": date_to,
                **extra,
            }
        )
        leave.action_approve()
        self.assertEqual(leave.state, "validate")
        return leave

    def _public_holiday(self, day, calendar=None):
        return self.env["resource.calendar.leaves"].create(
            {
                "name": "Public holiday",
                "calendar_id": calendar.id if calendar else False,
                "company_id": self.company.id,
                "date_from": datetime.combine(day, datetime.min.time()),
                "date_to": datetime.combine(day, datetime.max.time()),
            }
        )

    def _timesheets(self, source):
        return source.sudo().timesheet_ids.sorted("date_time")

    def _assert_entry(self, timesheet, day, begin, hours):
        self.assertEqual(timesheet.date, day)
        self.assertEqual(timesheet.time_begin, begin)
        self.assertAlmostEqual(timesheet.unit_amount, hours)
        self.assertEqual(timesheet.time_end, begin + hours)
        self.assertEqual(timesheet.project_id, self.project)
        self.assertEqual(timesheet.task_id, self.task)
        self.assertEqual(timesheet.employee_id, self.employee)

    def test_full_days_start_with_the_morning(self):
        leave = self._validate_leave(self.leave_type_day, self.monday, self.tuesday)
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 2)
        # 8 hours from 08:00 end at 16:00, before the working hours end.
        self._assert_entry(timesheets[0], self.monday, 8.0, 8.0)
        self._assert_entry(timesheets[1], self.tuesday, 8.0, 8.0)
        # Stored in UTC.
        self.assertEqual(timesheets[0].date_time, datetime(2026, 10, 5, 6, 0))
        self.assertEqual(timesheets[0].date_time_end, datetime(2026, 10, 5, 14, 0))
        self.assertAlmostEqual(leave.number_of_hours, 16.0)

    def test_morning_starts_with_the_morning(self):
        leave = self._validate_leave(
            self.leave_type_half_day,
            self.monday,
            self.monday,
            request_date_from_period="am",
            request_date_to_period="am",
        )
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 1)
        self._assert_entry(timesheets, self.monday, 8.0, 4.0)

    def test_afternoon_starts_with_the_afternoon(self):
        leave = self._validate_leave(
            self.leave_type_half_day,
            self.monday,
            self.monday,
            request_date_from_period="pm",
            request_date_to_period="pm",
        )
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 1)
        self._assert_entry(timesheets, self.monday, 13.0, 4.0)

    def test_hours_start_with_the_request(self):
        leave = self._validate_leave(
            self.leave_type_hour,
            self.monday,
            self.monday,
            request_hour_from=9.0,
            request_hour_to=15.0,
        )
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 1)
        # 3 + 2 working hours from 09:00.
        self._assert_entry(timesheets, self.monday, 9.0, 5.0)
        self.assertAlmostEqual(leave.number_of_hours, 5.0)

    def test_date_is_kept_for_an_approver_far_away(self):
        # 08:00 in Brussels is still the day before in Los Angeles.
        leave = self._validate_leave(
            self.leave_type_day,
            self.monday,
            self.monday,
            env=self.env(context=dict(self.env.context, tz="America/Los_Angeles")),
        )
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 1)
        self.assertEqual(timesheets.date, self.monday)
        self.assertEqual(timesheets.date_time, datetime(2026, 10, 5, 6, 0))

    def test_public_holiday_inside_leave_stays_free(self):
        self._public_holiday(self.tuesday, self.calendar)
        leave = self._validate_leave(self.leave_type_day, self.monday, self.tuesday)
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 1)
        self._assert_entry(timesheets, self.monday, 8.0, 8.0)

    def test_flexible_calendar_keeps_standard_entry(self):
        flexible = self.env["resource.calendar"].create(
            {
                "name": "Flexible",
                "tz": "Europe/Brussels",
                "flexible_hours": True,
                "hours_per_day": 8.0,
            }
        )
        self.employee.resource_calendar_id = flexible
        leave = self._validate_leave(self.leave_type_day, self.monday, self.monday)
        timesheets = self._timesheets(leave)
        self.assertEqual(len(timesheets), 1)
        self.assertEqual(timesheets.date, self.monday)
        self.assertAlmostEqual(timesheets.unit_amount, 8.0)

    def test_refuse_removes_every_entry(self):
        leave = self._validate_leave(self.leave_type_day, self.monday, self.tuesday)
        self.assertEqual(len(self._timesheets(leave)), 2)
        leave.action_refuse()
        self.assertFalse(leave.sudo().timesheet_ids)
        self.assertFalse(
            self.env["account.analytic.line"]
            .sudo()
            .search(
                [("employee_id", "=", self.employee.id), ("date", ">=", self.monday)]
            )
        )

    def test_public_holiday_on_calendar(self):
        holiday = self._public_holiday(self.monday, self.calendar)
        timesheets = self._timesheets(holiday).filtered(
            lambda line: line.employee_id == self.employee
        )
        self.assertEqual(len(timesheets), 1)
        self._assert_entry(timesheets, self.monday, 8.0, 8.0)
        self.assertEqual(timesheets.date_time, datetime(2026, 10, 5, 6, 0))
        self.assertEqual(timesheets.global_leave_id, holiday)

    def test_public_holiday_for_the_company(self):
        holiday = self._public_holiday(self.monday)
        timesheets = self._timesheets(holiday).filtered(
            lambda line: line.employee_id == self.employee
        )
        self.assertEqual(len(timesheets), 1)
        self._assert_entry(timesheets, self.monday, 8.0, 8.0)
        self.assertEqual(timesheets.global_leave_id, holiday)

    def test_public_holiday_regenerated_after_refusal(self):
        # Standard books the day for the leave and gives it to the public
        # holiday once the leave is refused; other modules may hand it over
        # right away. Either way the public holiday ends up with the entry.
        leave = self._validate_leave(self.leave_type_day, self.monday, self.tuesday)
        holiday = self._public_holiday(self.tuesday, self.calendar)
        leave.action_refuse()
        timesheets = self._timesheets(holiday).filtered(
            lambda line: line.employee_id == self.employee
        )
        self.assertEqual(len(timesheets), 1)
        self._assert_entry(timesheets, self.tuesday, 8.0, 8.0)

    def test_directly_prepared_entries_start_with_the_working_hours(self):
        # Other modules book public holiday entries from the prepared values
        # straight away, e.g. the personal ones of
        # hr_holidays_public_resource; the values carry the start already.
        holiday = self.env["resource.calendar.leaves"].create(
            {
                "name": "Personal public holiday",
                "calendar_id": self.calendar.id,
                "resource_id": self.employee.resource_id.id,
                "date_from": datetime(2026, 10, 4, 22, 0),
                "date_to": datetime(2026, 10, 5, 21, 59, 59),
            }
        )
        self.assertFalse(holiday.sudo().timesheet_ids)
        line = (
            self.env["account.analytic.line"]
            .sudo()
            .create(
                holiday._timesheet_prepare_line_values(
                    0, self.employee, [(self.monday, 8.0)], self.monday, 8.0
                )
            )
        )
        self.assertEqual(self._timesheets(holiday), line)
        self._assert_entry(line, self.monday, 8.0, 8.0)
