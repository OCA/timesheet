from datetime import date, datetime

import pytz

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env.ref("hr.employee_admin")
        cls.employee.tz = "Europe/Brussels"  # UTC+1/+2
        cls.project = cls.env["project.project"].create({"name": "Test Project"})

    def test_compute_time_by_datetime(self):
        aal = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "date_time": "2024-06-01 08:30:00",
                "date_time_end": "2024-06-01 10:30:00",
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )

        tz = pytz.timezone(self.employee.tz)
        offset = tz.utcoffset(aal.date_time)

        self.assertEqual(offset.total_seconds(), 2 * 3600)  # Assuming UTC+2
        self.assertEqual(aal.time_begin, 10.5)
        self.assertEqual(aal.time_end, 12.5)
        self.assertEqual(aal.unit_amount, 2.0)

    def test_compute_time_by_date_and_time(self):
        aal = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "date": "2024-06-01",
                "time_begin": 8.5,
                "time_end": 10.5,
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )

        tz = pytz.timezone(self.employee.tz)
        offset = tz.utcoffset(aal.date_time)

        self.assertEqual(offset.total_seconds(), 2 * 3600)  # Assuming UTC+2
        self.assertEqual(aal.date_time, datetime(2024, 6, 1, 6, 30, 0))
        self.assertEqual(aal.date_time_end, datetime(2024, 6, 1, 8, 30, 0))
        self.assertEqual(aal.unit_amount, 2.0)

    def test_compute_time_with_next_day(self):
        aal = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "date": "2024-06-01",
                "time_begin": 20.0,
                "unit_amount": 8.0,
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )

        tz = pytz.timezone(self.employee.tz)
        offset = tz.utcoffset(aal.date_time)

        self.assertEqual(offset.total_seconds(), 2 * 3600)  # Assuming UTC+2
        self.assertEqual(aal.date_time, datetime(2024, 6, 1, 18, 0, 0))
        self.assertEqual(aal.date_time_end, datetime(2024, 6, 2, 2, 0, 0))
        self.assertEqual(aal.unit_amount, 8.0)

    def test_compute_time_by_date_time_amount(self):
        aal = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "date": "2024-06-01",
                "time_begin": 8.5,
                "unit_amount": 2.0,
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )

        tz = pytz.timezone(self.employee.tz)
        offset = tz.utcoffset(aal.date_time)

        self.assertEqual(offset.total_seconds(), 2 * 3600)  # Assuming UTC+2
        self.assertEqual(aal.date_time, datetime(2024, 6, 1, 6, 30, 0))
        self.assertEqual(aal.date_time_end, datetime(2024, 6, 1, 8, 30, 0))
        self.assertEqual(aal.time_begin, 8.5)
        self.assertEqual(aal.time_end, 10.5)
        self.assertEqual(aal.unit_amount, 2.0)

    def test_compute_time_begin_employee_timezone(self):
        self.employee.tz = "America/New_York"
        aal = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "date_time": "2024-06-01 14:15:00",  # UTC
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )

        # In US/Eastern (UTC-4 in summer), 14:15 UTC = 10:15 local
        self.assertEqual(aal.time_begin, 10.25)

    def test_compute_time_begin_without_user_timezone(self):
        self.employee.tz = False
        self.env.user.tz = "America/New_York"
        aal = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "date_time": "2024-06-01 14:15:00",  # UTC
                "project_id": self.project.id,
                "employee_id": self.employee.id,
            }
        )

        # In US/Eastern (UTC-4 in summer), 14:15 UTC = 10:15 local
        self.assertEqual(aal.time_begin, 10.25)

    def test_onchange_time_begin(self):
        hour_uom = self.env.ref("uom.product_uom_hour")
        form = Form(
            self.env["account.analytic.line"].with_context(
                default_product_uom_id=hour_uom.id, default_employee_id=self.employee.id
            ),
            view=self.env.ref(
                "hr_timesheet_time_control_begin_end.hr_timesheet_line_form"
            ),
        )

        form.date = date(2023, 6, 1)
        form.time_begin = 8
        self.assertEqual(form.date_time, datetime(2023, 6, 1, 6, 0, 0))

    def test_onchange_time_end(self):
        hour_uom = self.env.ref("uom.product_uom_hour")
        form = Form(
            self.env["account.analytic.line"].with_context(
                default_product_uom_id=hour_uom.id, default_employee_id=self.employee.id
            ),
            view=self.env.ref(
                "hr_timesheet_time_control_begin_end.hr_timesheet_line_form"
            ),
        )

        form.date = date(2023, 6, 1)
        form.time_begin = 8
        form.time_end = 10
        self.assertEqual(form.date_time_end, datetime(2023, 6, 1, 8, 0, 0))
        self.assertEqual(form.unit_amount, 2.0)

    def test_onchange_time_end_calendar_context(self):
        self.employee.tz = "Europe/Berlin"  # UTC+1/+2 (same as Brussels)
        hour_uom = self.env.ref("uom.product_uom_hour")
        form = Form(
            self.env["account.analytic.line"].with_context(
                default_product_uom_id=hour_uom.id,
                lang="en_US",
                tz="Europe/Berlin",
                uid=self.env.user.id,
                allowed_company_ids=[self.env.company.id],
                grid_anchor="2025-10-22",
                group_expand=True,
                is_timesheet=1,
                default_employee_id=self.employee.id,
                is_my_timesheets=1,
                default_date_time="2025-10-20 03:15:00",
                default_date_time_end="2025-10-20 07:00:00",
                default_time_start=5.25,  # compatibility with hr_timesheet_begin_end
                default_time_stop=9.0,  # compatibility with hr_timesheet_begin_end
            ),
            view=self.env.ref(
                "hr_timesheet_time_control_begin_end.hr_timesheet_line_form"
            ),
        )

        self.assertEqual(form.date, date(2025, 10, 20))
        self.assertEqual(form.date_time, datetime(2025, 10, 20, 3, 15, 0))
        self.assertEqual(form.date_time_end, datetime(2025, 10, 20, 7, 0, 0))
        # Note: Time begin is computed from date_time using UTC timezone (3.25 = 3:15)
        self.assertEqual(form.time_begin, 5.25)
        self.assertEqual(form.time_end, 9.0)
        self.assertEqual(form.unit_amount, 3.75)

    def test_default_get_derives_date_from_datetime(self):
        """Date is derived from default_date_time (UTC) when default_date is absent."""
        start = datetime(2025, 6, 15, 23, 0, 0)
        vals = (
            self.env["account.analytic.line"]
            .with_context(
                default_date_time=start,
            )
            .default_get(["date", "date_time"])
        )
        self.assertEqual(vals.get("date"), date(2025, 6, 15))
        self.assertEqual(vals.get("date_time"), start)

    def test_default_get_accepts_dict_keys(self):
        """Play button passes _fields.keys() (dict_keys), which is not list-concatenable."""
        fields_list = self.env["account.analytic.line"]._fields.keys()
        vals = self.env["account.analytic.line"].default_get(fields_list)
        self.assertIsInstance(vals, dict)
        self.assertIn("date", vals)
