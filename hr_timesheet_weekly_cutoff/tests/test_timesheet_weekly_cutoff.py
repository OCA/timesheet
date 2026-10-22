from datetime import date
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTimesheetWeeklyCutoff(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )

    def _create_timesheet(self, entry_date):
        return self.env["account.analytic.line"].create(
            {
                "name": "Development",
                "date": entry_date,
                "unit_amount": 1.0,
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "task_id": self.task.id,
            }
        )

    def test_no_validation_when_cutoff_not_configured(self):
        """
        Verify that no weekly cutoff validation is applied
        when the company cutoff weekday is not configured.
        """
        self.company.timesheet_lock_weekday = False
        fake_today = date(2026, 5, 12)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            line = self._create_timesheet(date(2026, 5, 1))
        self.assertTrue(line)

    def test_allow_entries_during_cutoff_day(self):
        """
        Monday 2026-05-11 (cutoff day)

        Allowed:
        2026-05-05 -> 2026-05-11
        """
        self.company.timesheet_lock_weekday = "0"
        fake_today = date(2026, 5, 11)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            allowed_dates = [
                date(2026, 5, 5),
                date(2026, 5, 6),
                date(2026, 5, 7),
                date(2026, 5, 8),
                date(2026, 5, 9),
                date(2026, 5, 10),
                date(2026, 5, 11),
            ]
            for entry_date in allowed_dates:
                self._create_timesheet(entry_date)

    def test_block_entries_before_allowed_range_on_cutoff_day(self):
        """
        Monday 2026-05-11

        Block:
        2026-05-04 and earlier
        """
        self.company.timesheet_lock_weekday = "0"
        fake_today = date(2026, 5, 11)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            with self.assertRaises(ValidationError):
                self._create_timesheet(date(2026, 5, 4))

    def test_block_previous_week_after_cutoff_day(self):
        """
        Tuesday 2026-05-12

        Block:
        Monday 2026-05-11 and earlier
        """
        self.company.timesheet_lock_weekday = "0"
        fake_today = date(2026, 5, 12)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            blocked_dates = [
                date(2026, 5, 11),
                date(2026, 5, 10),
                date(2026, 5, 9),
            ]
            for entry_date in blocked_dates:
                with self.assertRaises(ValidationError):
                    self._create_timesheet(entry_date)

    def test_allow_current_week_after_cutoff_day(self):
        """
        Thursday 2026-05-14

        Allowed:
        2026-05-12 -> 2026-05-14
        """
        self.company.timesheet_lock_weekday = "0"
        fake_today = date(2026, 5, 14)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            allowed_dates = [
                date(2026, 5, 12),
                date(2026, 5, 13),
                date(2026, 5, 14),
            ]
            for entry_date in allowed_dates:
                self._create_timesheet(entry_date)

    def test_bypass_group_allows_registration(self):
        """
        Verify that users belonging to the bypass group
        can register timesheets outside the weekly cutoff period
        without raising a validation error.
        """
        self.company.timesheet_lock_weekday = "0"
        bypass_group = self.env.ref(
            "hr_timesheet_weekly_cutoff." "group_bypass_timesheet_lock"
        )
        self.env.user.groups_id |= bypass_group
        fake_today = date(2026, 5, 12)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            line = self._create_timesheet(date(2026, 5, 10))
        self.assertTrue(line)

    def test_bypass_group_marks_outside_weekly_cutoff(self):
        """
        Verify that timesheets registered outside the weekly
        cutoff period are marked as outside cutoff when the user
        belongs to the bypass group.
        """
        self.company.timesheet_lock_weekday = "0"
        bypass_group = self.env.ref(
            "hr_timesheet_weekly_cutoff." "group_bypass_timesheet_lock"
        )
        self.env.user.groups_id |= bypass_group
        fake_today = date(2026, 5, 12)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            line = self._create_timesheet(date(2026, 5, 10))
        self.assertTrue(line.is_outside_weekly_cutoff)

    def test_write_marks_outside_weekly_cutoff(self):
        """
        Verify that updating a timesheet date outside the allowed
        weekly cutoff period marks the record as outside cutoff
        when the user belongs to the bypass group.
        """
        self.company.timesheet_lock_weekday = "0"
        bypass_group = self.env.ref(
            "hr_timesheet_weekly_cutoff." "group_bypass_timesheet_lock"
        )
        self.env.user.groups_id |= bypass_group
        fake_today = date(2026, 5, 14)
        with patch(
            "odoo.fields.Date.context_today",
            return_value=fake_today,
        ):
            line = self._create_timesheet(date(2026, 5, 14))
            self.assertFalse(line.is_outside_weekly_cutoff)
            line.write(
                {
                    "date": date(2026, 5, 10),
                }
            )
        self.assertTrue(line.is_outside_weekly_cutoff)
