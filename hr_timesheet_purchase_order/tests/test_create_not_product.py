# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from odoo.exceptions import UserError
from odoo.tests.common import Form

from .common_po_recurrence import TestTimesheetPOrecurrenceCommon


class TestTimesheetPORecurrenceNotProduct(TestTimesheetPOrecurrenceCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        config_obj = cls.env["res.config.settings"]
        config = config_obj.create({"timesheet_product_id": False})
        config.execute()

    def test_recurrence_cron_repeat_until(self):
        """
        Test the cron job for the recurrence of the purchase
        order when the product is not defined
        """
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

            form.save()

            sheet_form = Form(self.hr_timesheet_sheet_obj.with_user(self.user_1))
            with sheet_form.timesheet_ids.new() as timesheet:
                timesheet.name = "test until month"
                timesheet.project_id = self.project
                timesheet.unit_amount = 1.0
            sheet_1 = sheet_form.save()
            self.assertFalse(sheet_1.purchase_order_id, msg="Must be equal False")

            # cannot create purchase order (sheet not approved)
            with self.assertRaises(UserError):
                sheet_1.action_create_purchase_order()

            sheet_1.action_timesheet_confirm()
            with self.assertRaises(
                UserError,
                msg=(
                    "You need to set a timesheet billing product"
                    "in settings in order to create a PO"
                ),
            ):
                sheet_1.action_create_purchase_order()
