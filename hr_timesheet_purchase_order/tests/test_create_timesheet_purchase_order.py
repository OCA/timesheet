# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import Form, SavepointCase


class TestHrTimesheetPurchaseOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product TEST",
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
        config_obj = cls.env["res.config.settings"]
        config = config_obj.create({"timesheet_product_id": cls.product.id})
        config.execute()

        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
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

        cls.employee = cls.employee_model.create(
            {
                "name": "Test Employee",
                "user_id": cls.user.id,
                "billing_partner_id": cls.user.partner_id.id,
                "allow_generate_purchase_order": True,
            }
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

    def test_create_purchase_order(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        with sheet_form.timesheet_ids.new() as timesheet:
            timesheet.name = "test"
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

        # cannot create purchase order (sheet not approved)
        with self.assertRaises(UserError):
            sheet.action_create_purchase_order()
        sheet.action_timesheet_done()
        self.assertEqual(sheet.state, "done")

        sheet.action_create_purchase_order()
        self.assertTrue(sheet.purchase_order_id)
        sheet.action_confirm_purchase_order()
        self.assertEqual(sheet.purchase_order_id.state, "purchase")
        action = sheet.action_open_purchase_order()
        self.assertTrue(action)
        self.assertTrue(sheet.purchase_order_id.timesheet_sheet_count > 0)
        action = sheet.purchase_order_id.action_open_timesheet_sheet()
        self.assertTrue(action)

    def test_create_purchase_order_access(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        with sheet_form.timesheet_ids.new() as timesheet:
            timesheet.name = "test"
            timesheet.project_id = self.project
        with sheet_form.timesheet_ids.edit(0) as timesheet:
            timesheet.unit_amount = 1.0
        sheet = sheet_form.save()
        self.employee.allow_generate_purchase_order = False
        self.assertFalse(sheet.purchase_order_id)
        with self.assertRaises(UserError):
            sheet.action_create_purchase_order()
        self.employee.billing_partner_id = False
        with self.assertRaises(UserError):
            sheet.action_create_purchase_order()
