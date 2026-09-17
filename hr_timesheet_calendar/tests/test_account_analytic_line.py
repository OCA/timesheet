from datetime import date, datetime, timedelta

from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_line_model = cls.env["account.analytic.line"]
        cls.test_user = cls.env.ref("base.user_admin")
        calendar = cls.env["resource.calendar"].create(
            {
                "name": "Test Calendar (6-15)",
                "tz": "Europe/Brussels",
                "attendance_ids": [
                    Command.create(
                        {
                            "name": "Mon AM",
                            "dayofweek": "0",
                            "hour_from": 8.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Mon PM",
                            "dayofweek": "0",
                            "hour_from": 13.0,
                            "hour_to": 15.0,
                            "day_period": "afternoon",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Tue AM",
                            "dayofweek": "1",
                            "hour_from": 8.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Tue PM",
                            "dayofweek": "1",
                            "hour_from": 13.0,
                            "hour_to": 15.0,
                            "day_period": "afternoon",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Wed AM",
                            "dayofweek": "2",
                            "hour_from": 8.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Wed PM",
                            "dayofweek": "2",
                            "hour_from": 13.0,
                            "hour_to": 15.0,
                            "day_period": "afternoon",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Thu AM",
                            "dayofweek": "3",
                            "hour_from": 8.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Thu PM",
                            "dayofweek": "3",
                            "hour_from": 13.0,
                            "hour_to": 15.0,
                            "day_period": "afternoon",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Fri AM",
                            "dayofweek": "4",
                            "hour_from": 8.0,
                            "hour_to": 12.0,
                            "day_period": "morning",
                        }
                    ),
                    Command.create(
                        {
                            "name": "Fri PM",
                            "dayofweek": "4",
                            "hour_from": 13.0,
                            "hour_to": 15.0,
                            "day_period": "afternoon",
                        }
                    ),
                ],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "resource_calendar_id": calendar.id,
                "tz": "Europe/Brussels",
            }
        )
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.task = cls.env["project.task"].create(
            {"name": "Test Task", "project_id": cls.project.id}
        )

        cls.analytic_line_model = cls.env["account.analytic.line"]
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.env["ir.config_parameter"].sudo().set_param(
            "hr_timesheet_time_control.timesheet_alignment", "no-gap"
        )

    @freeze_time("2025-04-02 23:00:00")
    def test_duplicate_today(self):
        # Create a sample analytic line record
        self.env.user.tz = "Europe/Brussels"
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Analytic Line",
                "date": date(2025, 4, 2),
                "date_time": datetime(2025, 4, 2, 9, 0),
                "date_time_end": datetime(2025, 4, 2, 17, 0),
                "project_id": self.project.id,
                "account_id": self.project.account_id.id,
                "employee_id": self.employee.id,
            }
        )

        # Call the method to duplicate the record
        new_record_id = self.analytic_line_model.duplicate_today(analytic_line.id)
        new_record = self.analytic_line_model.browse(new_record_id)

        # Assert the new record has today's date
        self.assertEqual(new_record.date, date(2025, 4, 3))

        # Assert the time components are preserved
        self.assertEqual(new_record.date_time, datetime(2025, 4, 3, 9, 0))
        self.assertEqual(new_record.date_time_end, datetime(2025, 4, 3, 17, 0))

        # Assert the new record is not the same as the original
        self.assertNotEqual(new_record.id, analytic_line.id)

    @freeze_time("2025-04-03 12:00:00")
    def test_duplicate_today_no_end(self):
        # Create a sample analytic line record
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Analytic Line",
                "date": date(2025, 4, 2),
                "date_time": datetime(2025, 4, 2, 9, 0),
                "project_id": self.project.id,
                "account_id": self.project.account_id.id,
                "employee_id": self.employee.id,
            }
        )

        # Call the method to duplicate the record
        new_record_id = self.analytic_line_model.duplicate_today(analytic_line.id)
        new_record = self.analytic_line_model.browse(new_record_id)

        # Assert the new record has today's date
        self.assertEqual(new_record.date, date(2025, 4, 3))

        # Assert the time components are preserved
        self.assertEqual(new_record.date_time, datetime(2025, 4, 3, 9, 0))
        self.assertEqual(new_record.date_time_end, datetime(2025, 4, 3, 9, 0))
        self.assertEqual(new_record.unit_amount, 0)

        # Assert the new record is not the same as the original
        self.assertNotEqual(new_record.id, analytic_line.id)

    @freeze_time("2025-04-02 12:00:00")
    def test_get_default_start_time_now(self):
        """Test the default start time calculation."""
        self.env["ir.config_parameter"].sudo().set_param(
            "hr_timesheet_time_control.timesheet_alignment", "now"
        )
        default_start_time = self.analytic_line_model._get_default_start_time()
        self.assertEqual(default_start_time, datetime(2025, 4, 2, 12, 0, 0))

    @freeze_time("2025-04-02 12:00:00")
    def test_get_default_start_time_calendar(self):
        """Test the default start time calculation."""
        default_start_time = self.analytic_line_model.with_context(
            default_employee_id=self.employee.id
        )._get_default_start_time()
        self.assertEqual(default_start_time, datetime(2025, 4, 2, 6, 0, 0))

    @freeze_time("2025-04-05 12:00:00")
    def test_get_default_start_time_no_working_hours(self):
        """Test the default start time calculation on days without working hours."""
        default_start_time = self.analytic_line_model.with_context(
            default_employee_id=self.employee.id
        )._get_default_start_time()
        self.assertEqual(default_start_time, datetime(2025, 4, 5, 12, 0, 0))

    @freeze_time("2025-04-05 12:00:00")
    def test_get_default_start_time_other_default_day(self):
        """Test the default start time calculation on days without working hours."""
        default_start_time = self.analytic_line_model.with_context(
            default_employee_id=self.employee.id, default_date=date(2025, 4, 1)
        )._get_default_start_time()
        self.assertEqual(default_start_time, datetime(2025, 4, 1, 6, 0, 0))

    @freeze_time("2025-04-01 12:00:10")
    def test_get_default_start_time_no_working_hours_other_default_day(self):
        """Test the default start time calculation on days without working hours."""
        default_start_time = self.analytic_line_model.with_context(
            default_employee_id=self.employee.id, default_date=date(2025, 4, 5)
        )._get_default_start_time()
        self.assertEqual(default_start_time, datetime(2025, 4, 5, 12, 0, 0))

    @freeze_time("2025-04-01 12:00:10")
    def test_get_default_start_time_no_employee_other_default_day(self):
        """Test the default start time calculation on days without working hours."""
        default_start_time = self.analytic_line_model.with_context(
            default_date=date(2025, 4, 5)
        )._get_default_start_time()
        self.assertEqual(default_start_time, datetime(2025, 4, 5, 12, 0, 0))

    @freeze_time("2025-04-02 12:00:00")
    def test_create_by_unit_amount(self):
        """Test the computation of date_time_end based on unit_amount."""
        # arrange
        self.analytic_line_model.create(
            [
                {
                    "name": "Test Line",
                    "employee_id": self.employee.id,
                    "date_time": datetime(2025, 4, 2, 14, 0, 0),
                    "date_time_end": datetime(2025, 4, 2, 15, 0, 0),
                    "product_uom_id": self.uom_hour.id,
                },
                {
                    "name": "Test Line 2",
                    "employee_id": self.employee.id,
                    "date_time": datetime(2025, 4, 2, 12, 0, 0),
                    "date_time_end": datetime(2025, 4, 2, 13, 0, 0),
                    "product_uom_id": self.uom_hour.id,
                },
            ]
        )
        # act
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Line",
                "employee_id": self.employee.id,
                "unit_amount": 2,
                "product_uom_id": self.uom_hour.id,
            }
        )
        # assert
        self.assertEqual(analytic_line.date, date(2025, 4, 2))
        self.assertEqual(analytic_line.date_time, datetime(2025, 4, 2, 15, 0, 0))
        self.assertEqual(analytic_line.date_time_end, datetime(2025, 4, 2, 17, 0, 0))
        self.assertEqual(analytic_line.unit_amount, 2)

    @freeze_time("2025-04-05 12:00:00")
    def test_compute_date_time_end(self):
        """Test the computation of date_time_end based on unit_amount."""
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Line",
                "employee_id": self.employee.id,
                "date_time": datetime(2025, 4, 2, 12, 0, 0),
                "unit_amount": 2,
                "product_uom_id": self.uom_hour.id,
            }
        )
        self.assertEqual(analytic_line.date, date(2025, 4, 2))
        self.assertEqual(analytic_line.date_time_end, datetime(2025, 4, 2, 14, 0, 0))

    @freeze_time("2025-04-05 12:00:00")
    def test_create_date_no_date_time(self):
        # arrange
        self.analytic_line_model.create(
            [
                {
                    "name": "Test Line",
                    "employee_id": self.employee.id,
                    "date_time": datetime(2025, 4, 2, 14, 0, 0),
                    "date_time_end": datetime(2025, 4, 2, 15, 0, 0),
                    "product_uom_id": self.uom_hour.id,
                },
                {
                    "name": "Test Line 2",
                    "employee_id": self.employee.id,
                    "date_time": datetime(2025, 4, 2, 12, 0, 0),
                    "date_time_end": datetime(2025, 4, 2, 13, 0, 0),
                    "product_uom_id": self.uom_hour.id,
                },
            ]
        )
        # act
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Line",
                "date": date(2025, 4, 2),
                "employee_id": self.employee.id,
                "unit_amount": 2,
                "product_uom_id": self.uom_hour.id,
            }
        )
        # assert
        self.assertEqual(analytic_line.date, date(2025, 4, 2))
        self.assertEqual(analytic_line.date_time, datetime(2025, 4, 2, 15, 0, 0))
        self.assertEqual(analytic_line.date_time_end, datetime(2025, 4, 2, 17, 0, 0))
        self.assertEqual(analytic_line.unit_amount, 2)

    def test_create_with_default_date_time(self):
        """Calender uses default_date_time as string"""
        analytic_line = self.analytic_line_model.with_context(
            default_date_time="2025-04-05 12:00:00"
        ).create(
            {
                "name": "Test Line",
                "employee_id": self.employee.id,
                "unit_amount": 2,
                "product_uom_id": self.uom_hour.id,
            }
        )
        self.assertEqual(analytic_line.date, date(2025, 4, 5))
        self.assertEqual(analytic_line.date_time_end, datetime(2025, 4, 5, 14, 0, 0))

    def test_compute_unit_amount(self):
        """Test the computation of date_time_end based on unit_amount."""
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Line",
                "employee_id": self.employee.id,
                "date_time": datetime(2025, 4, 2, 12, 0, 0),
                "date_time_end": datetime(2025, 4, 2, 14, 0, 0),
                "product_uom_id": self.uom_hour.id,
            }
        )
        self.assertEqual(analytic_line.unit_amount, 2)

    @freeze_time("2025-04-02 12:00:00")
    def test_button_end_work(self):
        """Test the button_end_work method."""
        start_time = fields.Datetime.now()
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Line",
                "employee_id": self.employee.id,
                "date_time": start_time,
                "unit_amount": 0,
                "product_uom_id": self.uom_hour.id,
            }
        )
        analytic_line.with_context(
            stop_dt=start_time + timedelta(hours=2)
        ).button_end_work()
        self.assertEqual(analytic_line.unit_amount, 2)
        self.assertEqual(analytic_line.date_time, datetime(2025, 4, 2, 12, 0, 0))

    def test_button_end_work_error(self):
        """Test that button_end_work raises an error if the timer is not running."""
        start_time = fields.Datetime.now()
        analytic_line = self.analytic_line_model.create(
            {
                "name": "Test Line",
                "employee_id": self.employee.id,
                "date_time": start_time,
                "unit_amount": 2,
                "product_uom_id": self.uom_hour.id,
            }
        )
        with self.assertRaises(UserError):
            analytic_line.button_end_work()

    def test_running_domain(self):
        """Test the _running_domain method."""
        domain = self.analytic_line_model._running_domain()
        self.assertIn(("date_time", "!=", False), domain)
        self.assertIn(("user_id", "=", self.env.user.id), domain)

    def test_default_get_with_is_timesheet_context(self):
        """Test default_get method with is_timesheet context."""
        company = self.env.company
        company.project_time_mode_id = self.uom_hour

        # Test with employee and is_timesheet context
        vals = self.analytic_line_model.with_context(
            is_timesheet=True, default_employee_id=self.employee.id
        ).default_get(["product_uom_id", "company_id", "employee_id"])
        self.assertEqual(vals["product_uom_id"], self.uom_hour.id)
        self.assertEqual(vals["company_id"], company.id)

        # Test with employee and is_timesheet context
        vals = self.analytic_line_model.with_context(
            is_timesheet=True, default_employee_id=self.employee.id
        ).default_get(["product_uom_id", "employee_id"])
        self.assertEqual(vals["product_uom_id"], self.uom_hour.id)
        self.assertNotIn("company_id", vals)

        # Test without employee and is_timesheet context
        vals = self.analytic_line_model.default_get(["product_uom_id"])
        self.assertNotIn("product_uom_id", vals)
        self.assertNotIn("company_id", vals)

    @freeze_time("2025-04-02 12:00:00")
    def test_default_get_calendar_context_with_end_time(self):
        """Test default_get with calendar context including end time."""
        start_time = datetime(2025, 4, 2, 14, 0, 0)
        end_time = datetime(2025, 4, 2, 16, 30, 0)  # 2.5 hours

        # Simulate calendar context with start and end times
        vals = self.analytic_line_model.with_context(
            default_date_time=start_time,
            default_date_time_end=end_time,
        ).default_get(["date_time", "date_time_end", "unit_amount"])

        # Check that end time is populated from context
        self.assertEqual(vals.get("date_time_end"), end_time)
        # Check that unit_amount is calculated correctly (2.5 hours)
        self.assertAlmostEqual(vals.get("unit_amount", 0), 2.5, places=5)
