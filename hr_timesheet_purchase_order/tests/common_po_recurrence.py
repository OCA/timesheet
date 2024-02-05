# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestTimesheetPOrecurrenceCommon(SavepointCase):
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

        cls.hr_timesheet_sheet_obj = cls.env["hr_timesheet.sheet"].with_context(
            tracking_disable=True
        )
        cls.project_obj = cls.env["project.project"]
        cls.project_task_obj = cls.env["project.task"]
        cls.hr_employee_obj = cls.env["hr.employee"]
        cls.hr_timesheet_recurrence_obj = cls.env["hr.timesheet.recurrence"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.aaa_model = cls.env["account.analytic.account"]
        cls.res_users_obj = cls.env["res.users"].with_context(no_reset_password=True)
        cls.res_partner_obj = cls.env["res.partner"]
        config_obj = cls.env["res.config.settings"]
        config = config_obj.create({"timesheet_product_id": cls.product.id})
        config.execute()

        officer_group = cls.env.ref("hr.group_hr_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        sheet_user_group = cls.env.ref("hr_timesheet.group_hr_timesheet_user")
        project_user_group = cls.env.ref("project.group_project_user")

        cls.account_payment_term_30days = cls.env.ref(
            "account.account_payment_term_30days"
        )
        cls.account_payment_method_manual_out = cls.env.ref(
            "account.account_payment_method_manual_out"
        )

        cls.user_1 = cls.res_users_obj.create(
            {
                "name": "Test User 1",
                "login": "test_user_1",
                "email": "test_1@oca.com",
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

        cls.user_2 = cls.res_users_obj.create(
            {
                "name": "Test User 2",
                "login": "test_user_2",
                "email": "test_2@oca.com",
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
        cls.user_3 = cls.res_users_obj.create(
            {
                "name": "Test User 3",
                "login": "test_user_3",
                "email": "test_3@oca.com",
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

        cls.project = cls.project_obj.create(
            {
                "name": "Project #1",
                "allow_timesheets": True,
                "user_id": cls.user_1.id,
            }
        )
        cls.task = cls.project_task_obj.create(
            {
                "name": "Task #1",
                "project_id": cls.project.id,
            }
        )

        cls.project_2 = cls.project_obj.create(
            {
                "name": "Project #2",
                "allow_timesheets": True,
                "user_id": cls.user_2.id,
            }
        )
        cls.task_2 = cls.project_task_obj.create(
            {
                "name": "Task #2",
                "project_id": cls.project_2.id,
            }
        )

        cls.project_3 = cls.project_obj.create(
            {
                "name": "Project #3",
                "allow_timesheets": True,
                "user_id": cls.user_3.id,
            }
        )
        cls.task_3 = cls.project_task_obj.create(
            {
                "name": "Task #3",
                "project_id": cls.project_3.id,
            }
        )

        cls.outsourcing_company = cls.res_partner_obj.create(
            {
                "name": "Outsourcing Company",
                "is_company": True,
            }
        )

        cls.employee_1 = cls.hr_employee_obj.create(
            {
                "name": "Test Employee #1",
                "user_id": cls.user_1.id,
                "billing_partner_id": cls.outsourcing_company.id,
                "allow_generate_purchase_order": True,
            }
        )
        cls.employee_2 = cls.hr_employee_obj.create(
            {
                "name": "Test Employee #2",
                "user_id": cls.user_2.id,
                "billing_partner_id": cls.outsourcing_company.id,
                "allow_generate_purchase_order": True,
            }
        )

        cls.employee_3 = cls.hr_employee_obj.create(
            {
                "name": "Test Employee #3",
                "user_id": cls.user_3.id,
                "billing_partner_id": cls.outsourcing_company.id,
                "allow_generate_purchase_order": True,
            }
        )
