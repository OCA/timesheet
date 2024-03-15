# Copyright 2024 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from unittest.mock import patch

from odoo.tests.common import Form, TransactionCase


class TestHrTimesheetSheetEmployeeCalendarPlanning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sheet_model = cls.env["hr_timesheet.sheet"]
        cls.project_model = cls.env["project.project"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.employee_model = cls.env["hr.employee"]
        cls.employee_calendar_model = cls.env["hr.employee.calendar"]
        cls.resource_calendar_model = cls.env["resource.calendar"]

        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.env.user.company_ids += cls.company

        cls.calendar_1 = cls.resource_calendar_model.create(
            {
                "name": "Test calendar 1",
                "attendance_ids": [],
            }
        )
        cls.calendar_2 = cls.resource_calendar_model.create(
            {
                "name": "Test calendar 2",
                "attendance_ids": [],
            }
        )

        for day in range(5):
            cls.calendar_1.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "12",
                    },
                ),
            ]
            cls.calendar_2.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "13",
                        "hour_to": "17",
                    },
                ),
            ]

        cls.user = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id)],
                }
            )
        )

        cls.employee = cls.employee_model.create(
            {
                "name": "Test Employee",
                "user_id": cls.user.id,
                "company_id": cls.user.company_id.id,
                "calendar_ids": False,
            }
        )
        cls.project = cls.project_model.create(
            {
                "name": "Project 1",
                "company_id": cls.user.company_id.id,
                "allow_timesheets": True,
                "user_id": cls.user.id,
            }
        )
        cls.sheet = Form(cls.sheet_model.with_user(cls.user)).save()
        cls.employee.calendar_ids = False

    def test_01_get_sheet_weeks_num(self):
        sheet = self.sheet
        sheet.write({"date_start": "2024-02-26", "date_end": "2024-03-03"})
        monday = datetime.strptime("2024-02-26", "%Y-%m-%d").date()
        monday2 = datetime.strptime("2024-03-04", "%Y-%m-%d").date()

        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 1)
        sheet.write({"date_end": "2024-03-04"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)
        sheet.write({"date_end": "2024-03-10"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)

        sheet.write({"date_end": "2024-03-11"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 3)
        sheet.write({"date_end": "2024-02-27"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 1)

        sheet.write({"date_end": "2024-02-26"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 1)
        sheet.write({"date_end": "2024-03-03", "date_start": "2024-02-28"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 1)

        sheet.write({"date_end": "2024-03-04"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)
        sheet.write({"date_end": "2024-03-10"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)

        sheet.write({"date_end": "2024-03-11"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 3)
        sheet.write({"date_start": "2024-03-03", "date_end": "2024-03-03"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 1)

        sheet.write({"date_end": "2024-03-04"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)
        sheet.write({"date_end": "2024-03-10"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)

        sheet.write({"date_end": "2024-03-11"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 3)
        sheet.write({"date_start": "2024-03-04"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday2)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)
        sheet.write({"date_start": "2024-03-05"})
        self.assertEqual(sheet.get_sheet_weeks_num()[0], monday2)
        self.assertEqual(sheet.get_sheet_weeks_num()[1], 2)

    def test_02_calculate_theoretical_hours_one_week(self):
        sheet = self.sheet
        sheet.write({"date_start": "2024-02-19", "date_end": "2024-02-25"})
        self.employee.calendar_ids = False

        self.employee_calendar_model.create(
            {
                "employee_id": self.employee.id,
                "calendar_id": self.calendar_1.id,
                "date_start": "2024-02-19",
                "date_end": "2024-03-03",
            }
        )
        self.employee_calendar_model.create(
            {
                "employee_id": self.employee.id,
                "calendar_id": self.calendar_2.id,
            }
        )

        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 1)
        self.assertTrue(
            all(
                hours == 0.0 if day in (5, 6) else hours == 8.0
                for week in theoretical_weekly_hours.values()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_end": "2024-02-21"})
        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 1)
        self.assertTrue(
            all(
                hours == 8.0 if day in (0, 1, 2) else hours == 0.0
                for week in theoretical_weekly_hours.values()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_end": "2024-02-26"})
        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 2)
        self.assertTrue(
            all(
                (hours == 0.0 if day in (5, 6) else hours == 8.0)
                if week_num == 0
                else (hours == 8.0 if day == 0 else hours == 0.0)
                for week_num, week in theoretical_weekly_hours.items()
                for day, hours in week.items()
            )
        )

    def test_03_calculate_theoretical_hours_one_week(self):
        sheet = self.sheet
        sheet.write({"date_start": "2024-02-19", "date_end": "2024-03-03"})
        self.employee.calendar_ids = False

        self.employee_calendar_model.create(
            {
                "employee_id": self.employee.id,
                "calendar_id": self.calendar_1.id,
                "date_start": "2024-02-19",
                "date_end": "2024-03-03",
            }
        )
        self.employee_calendar_model.create(
            {
                "employee_id": self.employee.id,
                "calendar_id": self.calendar_2.id,
            }
        )

        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 2)
        self.assertTrue(
            all(
                hours == 0.0 if day in (5, 6) else hours == 8.0
                for week in theoretical_weekly_hours.values()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_start": "2024-02-15"})
        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 3)
        self.assertTrue(
            all(
                (hours == 4.0 if day in (3, 4) else hours == 0.0)
                if week_num == 0
                else (hours == 8.0 if day not in (5, 6) else hours == 0.0)
                for week_num, week in theoretical_weekly_hours.items()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_end": "2024-03-05"})
        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 4)
        self.assertTrue(
            all(
                (hours == 4.0 if day in (3, 4) else hours == 0.0)
                if week_num == 0
                else (hours == 4.0 if day in (0, 1) else hours == 0.0)
                if week_num == 3
                else (hours == 8.0 if day not in (5, 6) else hours == 0.0)
                for week_num, week in theoretical_weekly_hours.items()
                for day, hours in week.items()
            )
        )

    def test_04_calculate_theoretical_hours_two_weeks(self):
        sheet = self.sheet
        sheet.write({"date_start": "2024-02-19", "date_end": "2024-03-03"})
        self.employee.calendar_ids = False
        calendar_1 = self.calendar_1
        calendar_1.write({"two_weeks_calendar": True, "attendance_ids": False})
        for day in range(5):
            calendar_1.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "12",
                        "week_type": "0",
                    },
                ),
            ]
        for day in range(5):
            calendar_1.attendance_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "10",
                        "week_type": "1",
                    },
                ),
            ]

        self.employee_calendar_model.create(
            {
                "employee_id": self.employee.id,
                "calendar_id": calendar_1.id,
                "date_start": "2024-02-12",
                "date_end": "2024-03-03",
            }
        )
        self.employee_calendar_model.create(
            {
                "employee_id": self.employee.id,
                "calendar_id": self.calendar_2.id,
            }
        )

        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 2)
        self.assertTrue(
            all(
                (hours == 8.0 if day not in (5, 6) else hours == 0.0)
                if week_num == 0
                else (hours == 6.0 if day not in (5, 6) else hours == 0.0)
                for week_num, week in theoretical_weekly_hours.items()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_start": "2024-02-14", "date_end": "2024-03-06"})
        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 4)
        self.assertTrue(
            all(
                (hours == 6.0 if day in (2, 3, 4) else hours == 0.0)
                if week_num == 0
                else (hours == 8.0 if day not in (5, 6) else hours == 0.0)
                if week_num == 1
                else (hours == 6.0 if day not in (5, 6) else hours == 0.0)
                if week_num == 2
                else (hours == 4.0 if day in (0, 1, 2) else hours == 0.0)
                for week_num, week in theoretical_weekly_hours.items()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_start": "2024-02-12", "date_end": "2024-02-25"})
        theoretical_weekly_hours = sheet._calculate_theoretical_hours()
        self.assertEqual(len(theoretical_weekly_hours), 2)
        self.assertTrue(
            all(
                (hours == 6.0 if day not in (5, 6) else hours == 0.0)
                if week_num == 0
                else (hours == 8.0 if day not in (5, 6) else hours == 0.0)
                for week_num, week in theoretical_weekly_hours.items()
                for day, hours in week.items()
            )
        )

    def test_05_calculate_real_hours(self):
        sheet = self.sheet
        sheet.write({"date_start": "2024-02-19", "date_end": "2024-03-03"})
        self.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 5,
                "date": "2024-02-19",
                "sheet_id": sheet.id,
            }
        )

        real_weekly_hours = sheet._calculate_real_hours()
        self.assertEqual(len(real_weekly_hours), 2)
        self.assertTrue(
            all(
                (hours == 5.0 if day == 0 else hours == 0.0)
                if week_num == 0
                else (hours == 0.0)
                for week_num, week in real_weekly_hours.items()
                for day, hours in week.items()
            )
        )

        self.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 2,
                "date": "2024-02-19",
                "sheet_id": sheet.id,
            }
        )
        self.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 5,
                "date": "2024-03-01",
                "sheet_id": sheet.id,
            }
        )

        real_weekly_hours = sheet._calculate_real_hours()
        self.assertEqual(len(real_weekly_hours), 2)
        self.assertTrue(
            all(
                (hours == 7.0 if day == 0 else hours == 0.0)
                if week_num == 0
                else (hours == 5.0 if day == 4 else hours == 0.0)
                for week_num, week in real_weekly_hours.items()
                for day, hours in week.items()
            )
        )

        sheet.write({"date_end": "2024-03-04", "date_start": "2024-02-18"})
        self.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
                "date": "2024-03-04",
                "sheet_id": sheet.id,
            }
        )

        real_weekly_hours = sheet._calculate_real_hours()
        self.assertEqual(len(real_weekly_hours), 4)
        self.assertTrue(
            all(
                (hours == 7.0 if day == 0 else hours == 0.0)
                if week_num == 1
                else (hours == 5.0 if day == 4 else hours == 0.0)
                if week_num == 2
                else (hours == 1.0 if day == 0 else hours == 0.0)
                if week_num == 3
                else hours == 0.0
                for week_num, week in real_weekly_hours.items()
                for day, hours in week.items()
            )
        )

    def test_06_compute_invalid_imputations(self):
        sheet = self.sheet
        theoretical_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        real_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}

        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertFalse(sheet.invalid_hours_per_day)
                self.assertFalse(sheet.invalid_hours_per_week)
                self.assertFalse(sheet.hours_no_working_day)

        theoretical_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        real_weekly_hours = {0: {0: 7, 1: 9, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertTrue(sheet.invalid_hours_per_day)
                self.assertFalse(sheet.invalid_hours_per_week)
                self.assertFalse(sheet.hours_no_working_day)

        theoretical_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        real_weekly_hours = {0: {0: 0, 1: 8, 2: 4, 3: 8, 4: 8, 5: 8, 6: 0}}
        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertTrue(sheet.invalid_hours_per_day)
                self.assertFalse(sheet.invalid_hours_per_week)
                self.assertTrue(sheet.hours_no_working_day)

        theoretical_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        real_weekly_hours = {0: {0: 8, 1: 9, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertTrue(sheet.invalid_hours_per_day)
                self.assertTrue(sheet.invalid_hours_per_week)
                self.assertFalse(sheet.hours_no_working_day)

        theoretical_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0}}
        real_weekly_hours = {0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 1, 6: 0}}
        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertTrue(sheet.invalid_hours_per_day)
                self.assertTrue(sheet.invalid_hours_per_week)
                self.assertTrue(sheet.hours_no_working_day)

    def test_07_compute_invalid_imputations_two_weeks(self):
        sheet = self.sheet
        theoretical_weekly_hours = {
            0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
            1: {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 0, 6: 0},
        }
        real_weekly_hours = {
            0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
            1: {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 0, 6: 0},
        }

        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertFalse(sheet.invalid_hours_per_day)
                self.assertFalse(sheet.invalid_hours_per_week)
                self.assertFalse(sheet.hours_no_working_day)

        theoretical_weekly_hours = {
            0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
            1: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
        }
        real_weekly_hours = {
            0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
            1: {0: 7, 1: 9, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
        }
        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertTrue(sheet.invalid_hours_per_day)
                self.assertFalse(sheet.invalid_hours_per_week)
                self.assertFalse(sheet.hours_no_working_day)

        theoretical_weekly_hours = {
            0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
            1: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
        }
        real_weekly_hours = {
            0: {0: 8, 1: 8, 2: 4, 3: 8, 4: 8, 5: 0, 6: 0},
            1: {0: 8, 1: 7, 2: 4, 3: 8, 4: 8, 5: 1, 6: 0},
        }
        with patch.object(
            type(self.env["hr_timesheet.sheet"]),
            "_calculate_theoretical_hours",
            return_value=theoretical_weekly_hours,
        ):
            with patch.object(
                type(self.env["hr_timesheet.sheet"]),
                "_calculate_real_hours",
                return_value=real_weekly_hours,
            ):
                sheet._compute_invalid_imputations()
                self.assertTrue(sheet.invalid_hours_per_day)
                self.assertFalse(sheet.invalid_hours_per_week)
                self.assertTrue(sheet.hours_no_working_day)
