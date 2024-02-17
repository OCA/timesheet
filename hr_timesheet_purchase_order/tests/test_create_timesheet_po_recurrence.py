# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from dateutil.rrule import FR, MO, SA, TH
from freezegun import freeze_time

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form

from .common_po_recurrence import TestTimesheetPOrecurrenceCommon


class TestTimesheetPOrecurrence(TestTimesheetPOrecurrenceCommon):
    def test_create_purchase_order_recurrence_simple(self):
        """Test the creation of the purchase order with the recurrence of the timesheet"""
        with freeze_time("2020-03-01"):
            form_employee_1 = Form(self.employee_1)
            form_employee_1.billing_partner_id = self.outsourcing_company
            form_employee_1.allow_generate_purchase_order = True
            form_employee_1.save()

            form_employee_2 = Form(self.employee_2)
            form_employee_2.billing_partner_id = self.outsourcing_company
            form_employee_2.allow_generate_purchase_order = True
            form_employee_2.save()

            form_employee_3 = Form(self.employee_3)
            form_employee_3.billing_partner_id = self.outsourcing_company
            form_employee_3.allow_generate_purchase_order = True
            form_employee_3.save()

            form_billing_partner = Form(self.outsourcing_company)
            form_billing_partner.is_auto_po_generate = True

            form_billing_partner.repeat_interval = 5
            form_billing_partner.repeat_unit = "month"
            form_billing_partner.repeat_type = "after"
            form_billing_partner.repeat_number = 10
            form_billing_partner.repeat_on_month = "date"
            form_billing_partner.repeat_day = "31"
            billing_partner = form_billing_partner.save()

            self.assertTrue(
                bool(billing_partner.is_auto_po_generate), "should enable a recurrence"
            )
            billing_partner.update(dict(repeat_interval=2, repeat_number=11))
            self.assertEqual(
                billing_partner.repeat_interval, 2, "recurrence should be updated"
            )
            self.assertEqual(
                billing_partner.repeat_number, 11, "recurrence should be updated"
            )
            self.assertEqual(
                billing_partner.recurrence_id.recurrence_left, 11, "Must be equal 11"
            )
            self.assertEqual(
                billing_partner.next_recurrence_date,
                date(2020, 3, 31),
                "Must be equal {dt}".format(dt=date(2020, 3, 31)),
            )
            self.assertEqual(
                billing_partner.recurrence_id.next_recurrence_date,
                date(2020, 3, 31),
                "Must be equal {dt}".format(dt=date(2020, 3, 31)),
            )
            self.assertEqual(
                billing_partner.next_recurrence_date,
                billing_partner.recurrence_id.next_recurrence_date,
                "Must be equal {dt}".format(dt=date(2020, 3, 31)),
            )
            billing_partner.is_auto_po_generate = False
            self.assertFalse(
                bool(billing_partner.is_auto_po_generate),
                "The recurrence should be disabled",
            )
            self.assertFalse(
                bool(billing_partner.recurrence_id), "The recurrence should be deleted"
            )
            # enabled is_auto_po_generate
            with Form(billing_partner) as form:
                form.is_auto_po_generate = True
                form.repeat_interval = 5
                form.repeat_unit = "month"
                form.repeat_type = "after"
                form.repeat_number = 10
                form.repeat_on_month = "date"
                form.repeat_day = "31"
                billing_partner = form.save()

            self.assertTrue(
                bool(billing_partner.recurrence_id), "The recurrence should be enabled"
            )
            sheet_form = Form(self.hr_timesheet_sheet_obj.with_user(self.user_1))
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
                self.hr_timesheet_recurrence_obj._cron_generate_auto_po()

    def test_onchange_repeat_day(self):
        """Check when the repeat day is set incorrectly"""
        with freeze_time("2020-02-01"):
            form = Form(self.outsourcing_company)
            form.is_auto_po_generate = True
            form.repeat_interval = 5
            form.repeat_unit = "month"
            form.repeat_type = "after"
            form.repeat_number = 10
            form.repeat_on_month = "date"
            form.repeat_day = -1
            billing_partner = form.save()
        self.assertEqual(billing_partner.repeat_day, 1, "Must be equal 1")

        with self.assertRaisesRegex(
            ValidationError,
            (
                (
                    "The number of days in a month cannot be negative "
                    "or more than %s days"
                )
                % -1
            ),
        ):
            billing_partner.recurrence_id.repeat_day = -1

    def test_recurrence_cron_repeat_after(self):
        """Test the cron method of the recurrence is correctly working"""
        with freeze_time("2020-01-01"):
            form = Form(self.outsourcing_company)
            form.name = "Test Employee recurrence cron_repeat_after"
            form.is_auto_po_generate = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "after"
            form.repeat_number = 2
            form.repeat_on_month = "date"
            form.repeat_day = "15"
            billing_partner = form.save()

            self.assertEqual(billing_partner.next_recurrence_date, date(2020, 1, 15))

            sheet_form = Form(self.hr_timesheet_sheet_obj.with_user(self.user_1))
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
            # self.assertEqual(len(employee.timesheet_sheet_ids), 1)
            self.hr_timesheet_recurrence_obj._cron_generate_auto_po()

        with freeze_time("2020-01-15"):
            self.hr_timesheet_recurrence_obj._cron_generate_auto_po()
        with freeze_time("2020-02-15"):
            self.hr_timesheet_recurrence_obj._cron_generate_auto_po()

    def test_recurrence_cron_repeat_until(self):
        """Check when the until date is set correctly and create purchase order"""
        with freeze_time("2020-01-01"):
            form = Form(self.outsourcing_company)
            form.is_auto_po_generate = True
            form.repeat_interval = 1
            form.repeat_unit = "month"
            form.repeat_type = "until"
            form.repeat_until = date(2020, 2, 20)
            form.repeat_on_month = "date"
            form.repeat_day = "15"

            form.property_supplier_payment_term_id = self.account_payment_term_30days
            form.property_payment_method_id = self.account_payment_method_manual_out
            form.receipt_reminder_email = True
            form.reminder_date_before_receipt = 3

            billing_partner = form.save()

            sheet_form = Form(self.hr_timesheet_sheet_obj.with_user(self.user_1))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test until month"
                timesheet.project_id = self.project
                timesheet.unit_amount = 1.0
            sheet_1 = sheet_form.save()
            self.assertFalse(sheet_1.purchase_order_id, msg="Must be equal False")

            sheet_form = Form(self.hr_timesheet_sheet_obj.with_user(self.user_2))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test until month"
                timesheet.project_id = self.project_2
                timesheet.unit_amount = 2.0
            sheet_2 = sheet_form.save()
            self.assertFalse(sheet_2.purchase_order_id, msg="Must be equal False")

            sheet_form = Form(self.hr_timesheet_sheet_obj.with_user(self.user_3))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test until month"
                timesheet.project_id = self.project_3
                timesheet.unit_amount = 2.0
            sheet_3 = sheet_form.save()
            self.assertFalse(sheet_3.purchase_order_id, msg="Must be equal False")

            # cannot create purchase order (sheet not approved)
            with self.assertRaises(UserError):
                sheet_1.action_create_purchase_order()

            with self.assertRaises(UserError):
                sheet_2.action_create_purchase_order()

            with self.assertRaises(UserError):
                sheet_3.action_create_purchase_order()

            sheet_1.action_timesheet_confirm()
            self.assertEqual(sheet_1.state, "confirm", msg="Must be equal confirm")
            sheet_1.action_timesheet_done()

            sheet_2.action_timesheet_confirm()
            self.assertEqual(sheet_2.state, "confirm", msg="Must be equal confirm")
            sheet_2.action_timesheet_done()

            self.assertEqual(len(self.employee_1.timesheet_sheet_ids), 1)
            self.assertEqual(len(self.employee_2.timesheet_sheet_ids), 1)
            self.assertEqual(len(self.employee_3.timesheet_sheet_ids), 1)

        self.assertEqual(
            billing_partner.recurrence_id.next_recurrence_date,
            date(2020, 1, 15),
            "Must be equal {dt}".format(dt=date(2020, 1, 15)),
        )

        with freeze_time("2020-01-15"):
            self.assertEqual(len(self.employee_1.timesheet_sheet_ids), 1)
            self.assertEqual(len(self.employee_2.timesheet_sheet_ids), 1)

            sheet_3.action_timesheet_confirm()
            self.assertEqual(sheet_3.state, "confirm", msg="Must be equal confirm")
            sheet_3.action_timesheet_done()

            self.assertEqual(len(self.employee_3.timesheet_sheet_ids), 1)
            self.hr_timesheet_recurrence_obj._cron_generate_auto_po()
            self.assertTrue(
                sheet_1.purchase_order_id, msg="Must be create new purchase order"
            )

            self.assertTrue(
                sheet_1.purchase_order_id.receipt_reminder_email,
                msg="Reminder email must be True",
            )
            self.assertEqual(
                sheet_1.purchase_order_id.payment_term_id,
                self.outsourcing_company.property_supplier_payment_term_id,
                msg=f"Must be equal {self.account_payment_term_30days.name}",
            )
            self.assertEqual(
                sheet_1.purchase_order_id.reminder_date_before_receipt,
                self.outsourcing_company.reminder_date_before_receipt,
                msg="Must be equal 3",
            )

            self.assertTrue(
                sheet_2.purchase_order_id, msg="Must be create new purchase order"
            )
            self.assertTrue(
                sheet_2.purchase_order_id.receipt_reminder_email,
                msg="Reminder email must be True",
            )
            self.assertEqual(
                sheet_2.purchase_order_id.payment_term_id,
                self.outsourcing_company.property_supplier_payment_term_id,
                msg=f"Must be equal {self.account_payment_term_30days.name}",
            )
            self.assertEqual(
                sheet_2.purchase_order_id.reminder_date_before_receipt,
                self.outsourcing_company.reminder_date_before_receipt,
                msg="Must be equal 3",
            )

            self.assertTrue(
                sheet_3.purchase_order_id, msg="Must be create new purchase order"
            )
            self.assertTrue(
                sheet_3.purchase_order_id.receipt_reminder_email,
                msg="Reminder email must be True",
            )
            self.assertEqual(
                sheet_3.purchase_order_id.payment_term_id,
                self.outsourcing_company.property_supplier_payment_term_id,
                msg=f"Must be equal {self.account_payment_term_30days.name}",
            )
            self.assertEqual(
                sheet_3.purchase_order_id.reminder_date_before_receipt,
                self.outsourcing_company.reminder_date_before_receipt,
                msg="Must be equal 3",
            )

            self.assertEqual(
                billing_partner.recurrence_id.next_recurrence_date,
                date(2020, 2, 15),
                "Must be equal {dt}".format(dt=date(2020, 2, 15)),
            )

        with freeze_time("2020-02-15"):
            self.hr_timesheet_recurrence_obj._cron_generate_auto_po()
            self.assertFalse(
                billing_partner.recurrence_id.next_recurrence_date,
                "Must be equal False",
            )

    def test_recurrence_week_day(self):
        """Check when the repeat interval is set incorrectly"""
        with self.assertRaisesRegex(
            ValidationError, (_("You should select a least one day"))
        ):
            form = Form(self.res_partner_obj)
            form.name = "Test Partner recurrence week_day"
            form.email = "test@partner.com"
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
        """Check when the repeat interval is set incorrectly"""
        with self.assertRaisesRegex(
            ValidationError, (_("The interval should be greater than 0"))
        ):
            form = Form(self.res_partner_obj)
            form.name = "Test Partner recurrence week_day"
            form.email = "test@partner.com"
            form.is_auto_po_generate = True
            form.repeat_interval = 0
            form.repeat_type = "after"
            form.save()

    def test_repeat_number(self):
        """Check when the repeat number is set incorrectly"""
        with self.assertRaisesRegex(
            ValidationError, (_("Should repeat at least once"))
        ):
            form = Form(self.res_partner_obj)
            form.name = "Test Partner recurrence"
            form.email = "test@partner.com"
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
        """Check when the until date is set incorrectly"""
        with freeze_time("2023-08-03"):
            with self.assertRaisesRegex(
                ValidationError, (_("The end date should be in the future"))
            ):
                form = Form(self.res_partner_obj)
                form.name = "Test Partner recurrence"
                form.email = "test@partner.com"
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
        """Test generate next dates for week"""
        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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

        start = date(2020, 1, 1)
        until = date(2020, 2, 1)
        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
            date_start=start,
            repeat_interval=3,
            repeat_unit="week",
            repeat_type="until",
            repeat_until=until,
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
        """Test generate next dates for month"""
        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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

        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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

        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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

        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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
        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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

        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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
        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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
        """Test generate recurring dates for yearly recurrence."""
        dates = self.hr_timesheet_recurrence_obj._get_next_recurring_dates(
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
