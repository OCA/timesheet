# Copyright 2026 OBS Solutions B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime
from unittest.mock import patch

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon

# Europe/Amsterdam is UTC+1 in winter: 08:00 UTC = 09:00 local.
TZ = "Europe/Amsterdam"


class TestBeginEndTimeControl(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="test-begin-end-timer",
            groups="hr_timesheet.group_hr_timesheet_user,project.group_project_manager",
            tz=TZ,
        )
        cls.user.action_create_employee()
        cls.user.employee_id.tz = TZ
        cls.project = (
            cls.env["project.project"]
            .with_user(cls.user)
            .create({"name": "Timer project", "allow_timesheets": True})
        )
        cls.Line = cls.env["account.analytic.line"].with_user(cls.user)

    def _timer(self, start, **vals):
        """A running timer started at ``start`` (naive UTC)."""
        return self.Line.create(
            dict(
                {
                    "name": "Timer",
                    "project_id": self.project.id,
                    "date_time": start,
                    "unit_amount": 0,
                },
                **vals,
            )
        )

    def assertHours(self, line, start, stop):
        self.assertAlmostEqual(line.time_start, start, places=4)
        self.assertAlmostEqual(line.time_stop, stop, places=4)

    def test_running_timer_has_no_hours(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        self.assertFalse(line.time_start)
        self.assertFalse(line.time_stop)

    def test_stop_fills_begin_end_in_employee_tz(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 9, 30)).button_end_work()
        self.assertAlmostEqual(line.unit_amount, 1.5)
        self.assertHours(line, 9.0, 10.5)

    def test_stop_keeps_seconds(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 8, 3, 49)).button_end_work()
        self.assertHours(line, 9.0, 9 + (3 * 60 + 49) / 3600)

    def test_consecutive_timers_get_hours(self):
        """Back-to-back timers do not overlap and both get their hours."""
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 10, 0)).button_end_work()
        follow_up = self._timer(datetime(2026, 1, 15, 10, 0))
        follow_up.with_context(stop_dt=datetime(2026, 1, 15, 11, 0)).button_end_work()
        self.assertHours(line, 9.0, 11.0)
        self.assertHours(follow_up, 11.0, 12.0)

    def test_timer_past_midnight_stops_without_hours(self):
        # 22:30 UTC = 23:30 local, stopped 01:30 local the next day.
        line = self._timer(datetime(2026, 1, 15, 22, 30))
        line.with_context(stop_dt=datetime(2026, 1, 16, 0, 30)).button_end_work()
        self.assertAlmostEqual(line.unit_amount, 2.0)
        self.assertFalse(line.time_start)
        self.assertFalse(line.time_stop)

    def test_overlap_stops_without_hours(self):
        self.Line.create(
            {
                "name": "Manual",
                "project_id": self.project.id,
                "date": date(2026, 1, 15),
                "time_start": 9.5,
                "time_stop": 10.0,
                "unit_amount": 0.5,
            }
        )
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 10, 0)).button_end_work()
        self.assertAlmostEqual(line.unit_amount, 2.0)
        self.assertFalse(line.time_start)

    def test_duration_change_moves_end_hour(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 9, 0)).button_end_work()
        line.unit_amount = 2.5
        self.assertHours(line, 9.0, 11.5)

    def test_end_time_change_moves_end_hour(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 9, 0)).button_end_work()
        line.date_time_end = datetime(2026, 1, 15, 9, 45)
        self.assertAlmostEqual(line.unit_amount, 1.75)
        self.assertHours(line, 9.0, 10.75)

    def test_begin_hour_change_moves_timer_start(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 9, 0)).button_end_work()
        line.write({"time_start": 8.0, "time_stop": 9.0, "unit_amount": 1.0})
        self.assertEqual(line.date_time, datetime(2026, 1, 15, 7, 0))
        self.assertEqual(line.date_time_end, datetime(2026, 1, 15, 8, 0))

    def test_manual_begin_end_line_sets_timer_start(self):
        line = self.Line.create(
            {
                "name": "Manual",
                "project_id": self.project.id,
                "date": date(2026, 1, 15),
                "time_start": 13.0,
                "time_stop": 14.5,
                "unit_amount": 1.5,
            }
        )
        self.assertEqual(line.date_time, datetime(2026, 1, 15, 12, 0))
        self.assertEqual(line.date_time_end, datetime(2026, 1, 15, 13, 30))

    def test_duration_only_line_gets_no_hours(self):
        """A line entered with a duration only keeps empty hours."""
        line = self.Line.create(
            {
                "name": "Duration only",
                "project_id": self.project.id,
                "date": date(2026, 1, 15),
                "unit_amount": 2.0,
            }
        )
        self.assertFalse(line.time_start)
        line.unit_amount = 3.0
        self.assertFalse(line.time_start)
        self.assertFalse(line.time_stop)

    def test_unworked_hours_move_end_hour(self):
        """Unworked time (e.g. a break) lies between begin and end."""
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        with patch.object(
            type(line), "_get_begin_end_unworked_hours", return_value=0.5
        ):
            hours = line._compute_begin_end_from_timer(datetime(2026, 1, 15, 8, 0), 4.0)
        self.assertAlmostEqual(hours[0], 9.0)
        self.assertAlmostEqual(hours[1], 13.5)

    def test_no_hours_without_start_or_duration(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        self.assertIsNone(line._compute_begin_end_from_timer(False, 1.0))
        self.assertIsNone(
            line._compute_begin_end_from_timer(datetime(2026, 1, 15, 8, 0), 0.0)
        )
        self.assertIsNone(
            line._compute_begin_end_from_timer(datetime(2026, 1, 15, 8, 0), -1.0)
        )

    def test_unworked_hours_hook(self):
        """The break being written wins over the stored one."""
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        self.assertEqual(line._get_begin_end_unworked_hours(), 0.0)
        self.assertEqual(
            line._get_begin_end_unworked_hours({"break_duration": 0.5}), 0.5
        )
        self.assertEqual(
            line._get_begin_end_unworked_hours({"break_duration": False}), 0.0
        )

    def test_write_begin_end_and_timer_start_together(self):
        """Explicit begin/end hours and timer start are written as given."""
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 9, 0)).button_end_work()
        line.write(
            {
                "date_time": datetime(2026, 1, 15, 6, 0),
                "time_start": 7.0,
                "time_stop": 8.0,
                "unit_amount": 1.0,
            }
        )
        self.assertEqual(line.date_time, datetime(2026, 1, 15, 6, 0))
        self.assertHours(line, 7.0, 8.0)

    def test_clear_begin_end_keeps_timer_start(self):
        line = self._timer(datetime(2026, 1, 15, 8, 0))
        line.with_context(stop_dt=datetime(2026, 1, 15, 9, 0)).button_end_work()
        line.write({"time_start": 0.0, "time_stop": 0.0})
        self.assertEqual(line.date_time, datetime(2026, 1, 15, 8, 0))
        self.assertFalse(line.time_start)

    def test_timer_start_change_on_line_without_hours(self):
        """Hours that cannot follow the timer are not invented on a write."""
        line = self._timer(datetime(2026, 1, 15, 22, 30))
        line.with_context(stop_dt=datetime(2026, 1, 16, 0, 30)).button_end_work()
        line.date_time = datetime(2026, 1, 15, 21, 0)
        self.assertFalse(line.time_start)
        self.assertFalse(line.time_stop)
