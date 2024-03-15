# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date, datetime

from odoo.tests.common import TransactionCase


class TestHrTimesheetSheet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = cls.env["res.users"]
        cls.employee_model = cls.env["hr.employee"]
        cls.timesheet_model = cls.env["hr_timesheet.sheet"]
        cls.account_analytic_line_model = cls.env["account.analytic.line"]
        cls.attendance_model = cls.env["hr.attendance"]
        cls.project_model = cls.env["project.project"]
        cls.task_model = cls.env["project.task"]
        cls.calendar_model = cls.env["resource.calendar"]

        cls.project = cls.project_model.create(
            {"name": "Test project", "allow_timesheets": True}
        )
        cls.task = cls.task_model.create(
            {"name": "Test task", "project_id": cls.project.id}
        )
        cls.calendar = cls.calendar_model.create(
            {
                "name": "Classic 40h/week",
                "tz": "UTC",
                "hours_per_day": 8.0,
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "dayofweek": "0",
                            "hour_from": 7,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Monday Afternoon",
                            "dayofweek": "0",
                            "hour_from": 13,
                            "hour_to": 16,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "dayofweek": "1",
                            "hour_from": 7,
                            "hour_to": 11,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Afternoon",
                            "dayofweek": "1",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "dayofweek": "2",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Afternoon",
                            "dayofweek": "2",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "dayofweek": "3",
                            "hour_from": 9,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Afternoon",
                            "dayofweek": "3",
                            "hour_from": 13,
                            "hour_to": 18,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "dayofweek": "4",
                            "hour_from": 9,
                            "hour_to": 13,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Afternoon",
                            "dayofweek": "4",
                            "hour_from": 13,
                            "hour_to": 17,
                        },
                    ),
                ],
            }
        )

        cls.user = cls.user_model.create(
            {
                "name": "Test User",
                "login": "test",
                "password": "test",
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.employee = cls.employee_model.create(
            {
                "name": "TestEmployee",
                "user_id": cls.user.id,
                "department_id": cls.env.ref("hr.dep_rd").id,
                "job_id": cls.env.ref("hr.job_developer").id,
                "work_email": "test@test.com",
                "work_phone": "+3281813700",
                "resource_calendar_id": cls.calendar.id,
            }
        )

        cls.timesheet = cls.timesheet_model.create(
            {
                "employee_id": cls.employee.id,
                "date_start": date(2024, 4, 8),
                "date_end": date(2024, 4, 14),
            }
        )

        cls.account_analytic_line_1 = cls.account_analytic_line_model.create(
            {
                "name": "Analytic Line 1",
                "employee_id": cls.employee.id,
                "date": date(2024, 4, 8),
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "amount": 6,
            }
        )
        cls.account_analytic_line_2 = cls.account_analytic_line_model.create(
            {
                "name": "Analytic Line 2",
                "employee_id": cls.employee.id,
                "date": date(2024, 4, 9),
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "amount": 10,
            }
        )
        cls.account_analytic_line_3 = cls.account_analytic_line_model.create(
            {
                "name": "Analytic Line 3",
                "employee_id": cls.employee.id,
                "date": date(2024, 4, 10),
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "amount": 2,
            }
        )
        cls.account_analytic_line_4 = cls.account_analytic_line_model.create(
            {
                "name": "Analytic Line 4",
                "employee_id": cls.employee.id,
                "date": date(2024, 4, 10),
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "amount": 3,
            }
        )
        cls.account_analytic_line_5 = cls.account_analytic_line_model.create(
            {
                "name": "Analytic Line 5",
                "employee_id": cls.employee.id,
                "date": date(2024, 4, 14),
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "amount": 10,
            }
        )

        cls.attendance_1 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 8, 8, 0, 0),
                "check_out": datetime(2024, 4, 8, 17, 0, 0),
            }
        )
        cls.attendance_2 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 12, 9, 0, 0),
                "check_out": datetime(2024, 4, 12, 13, 0, 0),
            }
        )
        cls.attendance_3 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 13, 10, 0, 0),
                "check_out": datetime(2024, 4, 13, 18, 0, 0),
            }
        )

    def test_generate_attendances_on_date(self):
        test_date = date(2024, 4, 9)
        result = self.timesheet._generate_attendances_on_date(test_date).sorted(
            "check_in"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].check_in, datetime(2024, 4, 9, 7))
        self.assertEqual(result[0].check_out, datetime(2024, 4, 9, 11))
        self.assertEqual(result[1].check_in, datetime(2024, 4, 9, 13))
        self.assertEqual(result[1].check_out, datetime(2024, 4, 9, 17))

        test_date = date(2024, 4, 10)
        result = self.timesheet._generate_attendances_on_date(test_date).sorted(
            "check_in"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].check_in, datetime(2024, 4, 10, 8))
        self.assertEqual(result[0].check_out, datetime(2024, 4, 10, 12))
        self.assertEqual(result[1].check_in, datetime(2024, 4, 10, 13))
        self.assertEqual(result[1].check_out, datetime(2024, 4, 10, 17))

        test_date = date(2024, 4, 14)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 0)

    def test_generate_attendances_on_date_two_week_calendar(self):
        two_week_calendar = self.calendar_model.create(
            {
                "name": "Two-week 20h/week",
                "tz": "UTC",
                "hours_per_day": 8.0,
                "two_weeks_calendar": True,
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "week_type": "0",
                            "dayofweek": "0",
                            "hour_from": 6,
                            "hour_to": 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "week_type": "0",
                            "dayofweek": "1",
                            "hour_from": 7,
                            "hour_to": 11,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "week_type": "0",
                            "dayofweek": "2",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "week_type": "0",
                            "dayofweek": "3",
                            "hour_from": 9,
                            "hour_to": 13,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "week_type": "0",
                            "dayofweek": "4",
                            "hour_from": 10,
                            "hour_to": 14,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Monday Morning",
                            "week_type": "1",
                            "dayofweek": "0",
                            "hour_from": 15,
                            "hour_to": 19,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Tuesday Morning",
                            "week_type": "1",
                            "dayofweek": "1",
                            "hour_from": 16,
                            "hour_to": 20,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Wednesday Morning",
                            "week_type": "1",
                            "dayofweek": "2",
                            "hour_from": 17,
                            "hour_to": 21,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Thursday Morning",
                            "week_type": "1",
                            "dayofweek": "3",
                            "hour_from": 18,
                            "hour_to": 22,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Friday Morning",
                            "week_type": "1",
                            "dayofweek": "4",
                            "hour_from": 19,
                            "hour_to": 23,
                        },
                    ),
                ],
            }
        )

        self.employee.write({"resource_calendar_id": two_week_calendar.id})
        self.timesheet.write({"date_end": date(2024, 4, 21)})

        test_date = date(2024, 4, 9)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].check_in, datetime(2024, 4, 9, 16))
        self.assertEqual(result[0].check_out, datetime(2024, 4, 9, 20))

        test_date = date(2024, 4, 10)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].check_in, datetime(2024, 4, 10, 17))
        self.assertEqual(result[0].check_out, datetime(2024, 4, 10, 21))

        test_date = date(2024, 4, 14)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 0)

        test_date = date(2024, 4, 16)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].check_in, datetime(2024, 4, 16, 7))
        self.assertEqual(result[0].check_out, datetime(2024, 4, 16, 11))

        test_date = date(2024, 4, 17)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].check_in, datetime(2024, 4, 17, 8))
        self.assertEqual(result[0].check_out, datetime(2024, 4, 17, 12))

        test_date = date(2024, 4, 21)
        result = self.timesheet._generate_attendances_on_date(test_date)
        self.assertEqual(len(result), 0)

    def test_get_employee_timezone(self):
        tz = self.timesheet._get_employee_timezone()
        self.assertEqual(tz.zone, "UTC")
        self.assertFalse(self.user.tz)
        self.user.write({"tz": "Europe/Chisinau"})
        tz = self.timesheet._get_employee_timezone()
        self.assertEqual(tz.zone, "Europe/Chisinau")
        self.assertEqual(tz.zone, self.user.tz)

    def test_missing_attendances(self):
        test_date = date(2024, 4, 8)
        self.assertFalse(self.timesheet._missing_attendances(test_date))
        test_date = date(2024, 4, 9)
        self.assertTrue(self.timesheet._missing_attendances(test_date))
        test_date = date(2024, 4, 10)
        self.assertTrue(self.timesheet._missing_attendances(test_date))
        test_date = date(2024, 4, 12)
        self.assertFalse(self.timesheet._missing_attendances(test_date))

        test_date = date(2024, 4, 14)
        self.assertTrue(self.timesheet._missing_attendances(test_date))
        self.attendance_3.write({"check_out": False})
        self.assertFalse(self.timesheet._missing_attendances(test_date))
