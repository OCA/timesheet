from datetime import date, datetime

from dateutil.rrule import FR, MO, SA, TH
from freezegun import freeze_time

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form, SavepointCase


class TestTimesheetPOrecurrence(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product recurrence",
                "default_code": "test",
            }
        )
        officer_group = cls.env.ref("hr.group_hr_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        sheet_user_group = cls.env.ref("hr_timesheet.group_hr_timesheet_user")
        project_user_group = cls.env.ref("project.group_project_user")
        cls.sheet_model = cls.env["hr_timesheet.sheet"].with_context(
            tracking_disable=True
        )
        cls.sheet_line_model = cls.env["hr_timesheet.sheet.line"]
        cls.project_model = cls.env["project.project"]
        cls.task_model = cls.env["project.task"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.aaa_model = cls.env["account.analytic.account"]
        cls.employee_model = cls.env["hr.employee"]
        cls.department_model = cls.env["hr.department"]
        cls.hr_timesheet_recurrence_model = cls.env["hr.timesheet.recurrence"]
        config_obj = cls.env["res.config.settings"]
        config = config_obj.create({"timesheet_product_id": cls.product.id})
        config.execute()

        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User recurrence",
                    "login": "test_user_recurrence",
                    "email": "test_recurrence@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                officer_group.id,
                                sheet_user_group.id,
                                project_user_group.id,
                                multi_company_group.id,
                            ],
                        )
                    ],
                }
            )
        )

        cls.project = cls.project_model.create(
            {
                "name": "Project",
                "allow_timesheets": True,
                "user_id": cls.user.id,
            }
        )
        cls.task = cls.task_model.create(
            {
                "name": "Task 1",
                "project_id": cls.project.id,
            }
        )

    def test_create_purchase_order_recurrence_simple(self):
        with freeze_time("2020-03-01"):
            form = Form(self.employee_model)
            form.name = "Test Employee recurrence"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True

            form.repeat_interval = 5
            form.repeat_unit = "month"
            form.repeat_type = "after"
            form.repeat_number = 10
            form.repeat_on_month = "date"
            form.repeat_day = "31"
            employee = form.save()

            self.assertTrue(
                bool(employee.is_auto_po_generate), "should enable a recurrence"
            )
            employee.update(dict(repeat_interval=2, repeat_number=11))
            self.assertEqual(
                employee.repeat_interval, 2, "recurrence should be updated"
            )
            self.assertEqual(employee.repeat_number, 11, "recurrence should be updated")
            self.assertEqual(
                employee.recurrence_id.recurrence_left, 11, "Must be equal 11"
            )
            self.assertEqual(
                employee.next_recurrence_date,
                date(2020, 3, 31),
                "Must be equal {dt}".format(dt=date(2020, 3, 31)),
            )
            self.assertEqual(
                employee.recurrence_id.next_recurrence_date,
                date(2020, 3, 31),
                "Must be equal {dt}".format(dt=date(2020, 3, 31)),
            )
            self.assertEqual(
                employee.next_recurrence_date,
                employee.recurrence_id.next_recurrence_date,
                "Must be equal {dt}".format(dt=date(2020, 3, 31)),
            )
            employee.is_auto_po_generate = False
            self.assertFalse(
                bool(employee.is_auto_po_generate), "The recurrence should be disabled"
            )
            self.assertFalse(
                bool(employee.recurrence_id), "The recurrence should be deleted"
            )
            # enabled is_auto_po_generate
            with Form(employee) as form:
                form.is_auto_po_generate = True
                form.repeat_interval = 5
                form.repeat_unit = "month"
                form.repeat_type = "after"
                form.repeat_number = 10
                form.repeat_on_month = "date"
                form.repeat_day = "31"
                employee = form.save()

            self.assertTrue(
                bool(employee.recurrence_id), "The recurrence should be enabled"
            )
            sheet_form = Form(self.sheet_model.with_user(self.user))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test1"
                timesheet.project_id = self.project

            with sheet_form.timesheet_ids.edit(0) as timesheet:
                timesheet.unit_amount = 1.0

            sheet = sheet_form.save()
            self.assertFalse(sheet.purchase_order_id)
            sheet.action_timesheet_confirm()
            self.assertEqual(sheet.state, "confirm")
            sheet.action_timesheet_done()
            with freeze_time("2020-02-29"):
                self.hr_timesheet_recurrence_model._cron_generate_auto_po()

    def test_onchange_repeat_day(self):
        with freeze_time("2020-02-01"):
            form = Form(self.employee_model)
            form.name = "Test Employee recurrence"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True

            form.repeat_interval = 5
            form.repeat_unit = "month"
            form.repeat_type = "after"
            form.repeat_number = 10
            form.repeat_on_month = "date"
            form.repeat_day = -1
            employee = form.save()
        self.assertEqual(employee.repeat_day, 1, "Must be equal 1")

        with self.assertRaisesRegex(
            ValidationError,
            (
                _(
                    "The number of days in a month cannot be negative "
                    "or more than 31 days"
                )
            ),
        ):
            employee.recurrence_id.repeat_day = -1

    def test_recurrence_cron_repeat_after(self):
        with freeze_time("2020-01-01"):
            form = Form(self.employee_model)
            form.name = "Test Employee recurrence cron_repeat_after"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "after"
            form.repeat_number = 2
            form.repeat_on_month = "date"
            form.repeat_day = "15"
            employee = form.save()

            self.assertEqual(employee.next_recurrence_date, date(2020, 1, 15))

            sheet_form = Form(self.sheet_model.with_user(self.user))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test2"
                timesheet.project_id = self.project

            with sheet_form.timesheet_ids.edit(0) as timesheet:
                timesheet.unit_amount = 1.0

            sheet = sheet_form.save()
            self.assertFalse(sheet.purchase_order_id)

            # cannot create purchase order (sheet not approved)
            with self.assertRaises(UserError):
                sheet.action_create_purchase_order()
            sheet.action_timesheet_confirm()
            self.assertEqual(sheet.state, "confirm")
            sheet.action_timesheet_done()
            self.assertEqual(len(employee.timesheet_sheet_ids), 1)
            self.hr_timesheet_recurrence_model._cron_generate_auto_po()

        with freeze_time("2020-01-15"):
            self.hr_timesheet_recurrence_model._cron_generate_auto_po()
        with freeze_time("2020-02-15"):
            self.hr_timesheet_recurrence_model._cron_generate_auto_po()

    def test_recurrence_cron_repeat_until(self):
        with freeze_time("2020-01-01"):
            form = Form(self.employee_model)
            form.name = "test recurring task"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True

            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "until"
            form.repeat_until = date(2020, 2, 20)
            form.repeat_on_month = "date"
            form.repeat_day = "15"
            employee = form.save()

            sheet_form = Form(self.sheet_model.with_user(self.user))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test until month"
                timesheet.project_id = self.project

            with sheet_form.timesheet_ids.edit(0) as timesheet:
                timesheet.unit_amount = 1.0

            sheet = sheet_form.save()
            self.assertFalse(sheet.purchase_order_id)

            # cannot create purchase order (sheet not approved)
            with self.assertRaises(UserError):
                sheet.action_create_purchase_order()
            sheet.action_timesheet_confirm()
            self.assertEqual(sheet.state, "confirm")
            sheet.action_timesheet_done()
            self.assertEqual(len(employee.timesheet_sheet_ids), 1)

        self.assertEqual(
            employee.recurrence_id.next_recurrence_date,
            date(2020, 1, 15),
            "Must be equal {dt}".format(dt=date(2020, 1, 15)),
        )

        with freeze_time("2020-01-15"):
            self.assertEqual(len(employee.timesheet_sheet_ids), 1)
            self.hr_timesheet_recurrence_model._cron_generate_auto_po()
            self.assertEqual(
                employee.recurrence_id.next_recurrence_date,
                date(2020, 2, 15),
                "Must be equal {dt}".format(dt=date(2020, 2, 15)),
            )

        with freeze_time("2020-02-15"):
            self.hr_timesheet_recurrence_model._cron_generate_auto_po()
            self.assertFalse(
                employee.recurrence_id.next_recurrence_date,
                "Must be equal False",
            )

    def test_recurrence_week_day(self):
        with self.assertRaisesRegex(
            ValidationError, (_("You should select a least one day"))
        ):
            form = Form(self.employee_model)
            form.name = "Test Employee recurrence week_day"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True
            form.repeat_interval = 1
            form.repeat_unit = "week"
            form.repeat_type = "after"
            form.repeat_number = 2
            form.mon = False
            form.tue = False
            form.wed = False
            form.thu = False
            form.fri = False
            form.sat = False
            form.sun = False
            form.save()

    def test_recurrence_repeat_interval(self):
        with self.assertRaisesRegex(
            ValidationError, (_("The interval should be greater than 0"))
        ):
            form = Form(self.employee_model)
            form.name = "Test Employee recurrence week_day"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True
            form.repeat_interval = 0
            form.repeat_type = "after"
            form.save()

    def test_repeat_number(self):
        with self.assertRaisesRegex(
            ValidationError, (_("Should repeat at least once"))
        ):
            form = Form(self.employee_model)
            form.name = "Test Employee recurrence"
            form.user_id = self.user
            form.billing_partner_id = self.user.partner_id
            form.allow_generate_purchase_order = True
            form.is_auto_po_generate = True
            form.repeat_interval = 1
            form.repeat_type = "after"
            form.repeat_number = 0
            form.mon = True
            form.tue = False
            form.wed = False
            form.thu = False
            form.fri = False
            form.sat = False
            form.sun = False
            form.save()

    def test_repeat_until_date(self):
        with freeze_time("2023-08-03"):
            with self.assertRaisesRegex(
                ValidationError, (_("The end date should be in the future"))
            ):
                form = Form(self.employee_model)
                form.name = "Test Employee recurrence"
                form.user_id = self.user
                form.billing_partner_id = self.user.partner_id
                form.allow_generate_purchase_order = True
                form.is_auto_po_generate = True
                form.repeat_interval = 1
                form.repeat_type = "until"
                form.repeat_until = "2023-08-01"
                form.mon = False
                form.tue = False
                form.wed = False
                form.thu = True
                form.fri = False
                form.sat = False
                form.sun = False
                form.save()

    def test_recurrence_next_dates_week(self):
        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2020, 1, 1),
            repeat_interval=1,
            repeat_unit="week",
            repeat_type=False,
            repeat_until=False,
            repeat_on_month=False,
            repeat_on_year=False,
            weekdays=False,
            repeat_day=False,
            repeat_week=False,
            repeat_month=False,
            count=5,
        )

        self.assertEqual(dates[0], datetime(2020, 1, 6, 0, 0))
        self.assertEqual(dates[1], datetime(2020, 1, 13, 0, 0))
        self.assertEqual(dates[2], datetime(2020, 1, 20, 0, 0))
        self.assertEqual(dates[3], datetime(2020, 1, 27, 0, 0))
        self.assertEqual(dates[4], datetime(2020, 2, 3, 0, 0))

        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2020, 1, 1),
            repeat_interval=3,
            repeat_unit="week",
            repeat_type="until",
            repeat_until=date(2020, 2, 1),
            repeat_on_month=False,
            repeat_on_year=False,
            weekdays=[MO, FR],
            repeat_day=False,
            repeat_week=False,
            repeat_month=False,
            count=100,
        )

        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], datetime(2020, 1, 3, 0, 0))
        self.assertEqual(dates[1], datetime(2020, 1, 20, 0, 0))
        self.assertEqual(dates[2], datetime(2020, 1, 24, 0, 0))

    def test_recurrence_next_dates_month(self):
        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2020, 1, 15),
            repeat_interval=1,
            repeat_unit="month",
            repeat_type=False,  # Forever
            repeat_until=False,
            repeat_on_month="date",
            repeat_on_year=False,
            weekdays=False,
            repeat_day=31,
            repeat_week=False,
            repeat_month=False,
            count=12,
        )

        # should take the last day of each month
        self.assertEqual(dates[0], date(2020, 1, 31))
        self.assertEqual(dates[1], date(2020, 2, 29))
        self.assertEqual(dates[2], date(2020, 3, 31))
        self.assertEqual(dates[3], date(2020, 4, 30))
        self.assertEqual(dates[4], date(2020, 5, 31))
        self.assertEqual(dates[5], date(2020, 6, 30))
        self.assertEqual(dates[6], date(2020, 7, 31))
        self.assertEqual(dates[7], date(2020, 8, 31))
        self.assertEqual(dates[8], date(2020, 9, 30))
        self.assertEqual(dates[9], date(2020, 10, 31))
        self.assertEqual(dates[10], date(2020, 11, 30))
        self.assertEqual(dates[11], date(2020, 12, 31))

        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2020, 2, 20),
            repeat_interval=3,
            repeat_unit="month",
            repeat_type=False,  # Forever
            repeat_until=False,
            repeat_on_month="date",
            repeat_on_year=False,
            weekdays=False,
            repeat_day=29,
            repeat_week=False,
            repeat_month=False,
            count=5,
        )

        self.assertEqual(dates[0], date(2020, 2, 29))
        self.assertEqual(dates[1], date(2020, 5, 29))
        self.assertEqual(dates[2], date(2020, 8, 29))
        self.assertEqual(dates[3], date(2020, 11, 29))
        self.assertEqual(dates[4], date(2021, 2, 28))

        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2020, 1, 10),
            repeat_interval=1,
            repeat_unit="month",
            repeat_type="until",
            repeat_until=datetime(2020, 5, 31),
            repeat_on_month="day",
            repeat_on_year=False,
            weekdays=[
                SA(4),
            ],  # 4th Saturday
            repeat_day=29,
            repeat_week=False,
            repeat_month=False,
            count=6,
        )

        self.assertEqual(len(dates), 5)
        self.assertEqual(dates[0], datetime(2020, 1, 25))
        self.assertEqual(dates[1], datetime(2020, 2, 22))
        self.assertEqual(dates[2], datetime(2020, 3, 28))
        self.assertEqual(dates[3], datetime(2020, 4, 25))
        self.assertEqual(dates[4], datetime(2020, 5, 23))

        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=datetime(2020, 1, 10),
            repeat_interval=6,  # twice a year
            repeat_unit="month",
            repeat_type="until",
            repeat_until=datetime(2021, 1, 11),
            repeat_on_month="date",
            repeat_on_year=False,
            weekdays=[TH(+1)],
            repeat_day=3,  # the 3rd of the month
            repeat_week=False,
            repeat_month=False,
            count=1,
        )

        self.assertEqual(len(dates), 2)
        self.assertEqual(dates[0], datetime(2020, 7, 3))
        self.assertEqual(dates[1], datetime(2021, 1, 3))

        # Should generate a date at the last day of the current month
        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2022, 2, 26),
            repeat_interval=1,
            repeat_unit="month",
            repeat_type="until",
            repeat_until=date(2022, 2, 28),
            repeat_on_month="date",
            repeat_on_year=False,
            weekdays=False,
            repeat_day=31,
            repeat_week=False,
            repeat_month=False,
            count=5,
        )

        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0], date(2022, 2, 28))

        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2022, 11, 26),
            repeat_interval=3,
            repeat_unit="month",
            repeat_type="until",
            repeat_until=date(2024, 2, 29),
            repeat_on_month="date",
            repeat_on_year=False,
            weekdays=False,
            repeat_day=25,
            repeat_week=False,
            repeat_month=False,
            count=5,
        )

        self.assertEqual(len(dates), 5)
        self.assertEqual(dates[0], date(2023, 2, 25))
        self.assertEqual(dates[1], date(2023, 5, 25))
        self.assertEqual(dates[2], date(2023, 8, 25))
        self.assertEqual(dates[3], date(2023, 11, 25))
        self.assertEqual(dates[4], date(2024, 2, 25))

        # Use the exact same parameters than the previous test
        # but with a repeat_day that is not passed yet
        # So we generate an additional date in the current month
        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2022, 11, 26),
            repeat_interval=3,
            repeat_unit="month",
            repeat_type="until",
            repeat_until=date(2024, 2, 29),
            repeat_on_month="date",
            repeat_on_year=False,
            weekdays=False,
            repeat_day=31,
            repeat_week=False,
            repeat_month=False,
            count=5,
        )

        self.assertEqual(len(dates), 6)
        self.assertEqual(dates[0], date(2022, 11, 30))
        self.assertEqual(dates[1], date(2023, 2, 28))
        self.assertEqual(dates[2], date(2023, 5, 31))
        self.assertEqual(dates[3], date(2023, 8, 31))
        self.assertEqual(dates[4], date(2023, 11, 30))
        self.assertEqual(dates[5], date(2024, 2, 29))

    def test_recurrence_next_dates_year(self):
        dates = self.hr_timesheet_recurrence_model._get_next_recurring_dates(
            date_start=date(2020, 12, 1),
            repeat_interval=1,
            repeat_unit="year",
            repeat_type="until",
            repeat_until=datetime(2026, 1, 1),
            repeat_on_month=False,
            repeat_on_year="date",
            weekdays=False,
            repeat_day=31,
            repeat_week=False,
            repeat_month="november",
            count=10,
        )

        self.assertEqual(len(dates), 5)
        self.assertEqual(dates[0], datetime(2021, 11, 30))
        self.assertEqual(dates[1], datetime(2022, 11, 30))
        self.assertEqual(dates[2], datetime(2023, 11, 30))
        self.assertEqual(dates[3], datetime(2024, 11, 30))
        self.assertEqual(dates[4], datetime(2025, 11, 30))
