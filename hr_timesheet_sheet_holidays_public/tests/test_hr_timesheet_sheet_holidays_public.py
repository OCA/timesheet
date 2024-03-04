# Copyright 2024 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo.tests.common import Form, TransactionCase


class TestHrTimesheetSheetEmployeeCalendarPlanning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sheet_model = cls.env["hr_timesheet.sheet"]
        cls.project_model = cls.env["project.project"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.employee_model = cls.env["hr.employee"]

        cls.public_holidays_model = cls.env["hr.holidays.public"]
        cls.holiday_model_line = cls.env["hr.holidays.public.line"]
        cls.leave_model = cls.env["hr.leave"]
        cls.leave_type_model = cls.env["hr.leave.type"]
        cls.global_leave_model = cls.env["resource.calendar.leaves"]

        cls.env["res.config.settings"].write(
            {"module_project_timesheet_holidays": True}
        )
        cls.company = cls.env.ref("base.main_company")
        cls.company.write({"internal_project_id": 5, "leave_timesheet_task_id": 38})

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
                "address_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "Test Employee Address",
                        "country_id": cls.env.ref("base.es").id,
                    }
                )
                .id,
            }
        )

        cls.project = cls.project_model.create(
            {
                "name": "Test Project",
                "company_id": cls.user.company_id.id,
                "allow_timesheets": True,
                "user_id": cls.user.id,
            }
        )
        cls.sheet = Form(cls.sheet_model.with_user(cls.user)).save()
        cls.sheet.write({"date_start": "2024-03-04", "date_end": "2024-03-10"})

        cls.public_holiday_year = cls.public_holidays_model.create(
            {"year": 2024, "country_id": cls.env.ref("base.es").id}
        )
        cls.public_holiday_day = cls.holiday_model_line.create(
            {
                "name": "Test Holiday",
                "date": "2024-03-07",
                "year_id": cls.public_holiday_year.id,
            }
        )
        cls.holiday_type = cls.leave_type_model.create(
            {"name": "Leave Type Test", "exclude_public_holidays": False}
        )

    def test_01_compute_hours_on_public_holiday(self):
        self.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 5,
                "date": "2024-03-04",
                "sheet_id": self.sheet.id,
            }
        )
        self.sheet._compute_hours_on_public_holiday()
        self.assertFalse(self.sheet.hours_on_public_holiday)

        holiday_line = self.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
                "unit_amount": 0,
                "date": "2024-03-07",
                "sheet_id": self.sheet.id,
            }
        )
        self.sheet._compute_hours_on_public_holiday()
        self.assertFalse(self.sheet.hours_on_public_holiday)
        holiday_line.write({"unit_amount": 5.0})

        self.sheet._compute_hours_on_public_holiday()
        self.assertTrue(self.sheet.hours_on_public_holiday)
        self.assertTrue(
            self.sheet.timesheet_ids.filtered(
                lambda ts: ts.date == datetime.date(2024, 3, 7)
                and ts.unit_amount != 0.0
            )
        )

    def test_02_compute_hours_on_public_holiday(self):
        personal_holiday = self.leave_model.create(
            {
                "date_from": "2024-03-06 00:00:00",
                "date_to": "2024-03-08 23:59:59",
                "holiday_status_id": self.holiday_type.id,
                "employee_id": self.employee.id,
            }
        )
        personal_holiday.action_validate()
        self.sheet._compute_hours_on_public_holiday()
        self.assertFalse(self.sheet.hours_on_public_holiday)
        self.assertTrue(
            self.sheet.timesheet_ids.filtered(
                lambda ts: ts.date == datetime.date(2024, 3, 7)
                and ts.unit_amount != 0.0
            )
        )

    def test_03_compute_hours_on_public_holiday(self):
        global_leave = self.global_leave_model.create(
            {
                "name": "Test leave",
                "resource_id": self.employee.resource_id.id,
                "date_from": "2024-03-06",
                "date_to": "2024-03-08",
                "calendar_id": self.employee.resource_calendar_id.id,
            }
        )
        self.sheet._compute_hours_on_public_holiday()
        self.assertFalse(self.sheet.hours_on_public_holiday)
        self.assertFalse(
            self.sheet.timesheet_ids.filtered(
                lambda ts: ts.date == datetime.date(2024, 3, 7)
                and ts.unit_amount != 0.0
            )
        )

        global_leave.write({"resource_id": False, "date_to": "2024-03-09"})
        self.sheet._compute_hours_on_public_holiday()
        self.assertFalse(self.sheet.hours_on_public_holiday)
        self.assertTrue(
            self.sheet.timesheet_ids.filtered(
                lambda ts: ts.date == datetime.date(2024, 3, 7)
                and ts.unit_amount != 0.0
            )
        )
