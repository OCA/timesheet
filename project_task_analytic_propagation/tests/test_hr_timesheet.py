# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)
import requests

from odoo.tests import new_test_user, tagged, users

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@tagged("-at_install", "post_install")
class HrTimesheet(TestCommonSaleTimesheet):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.analytic_user = new_test_user(
            cls.env, "test_user", "analytic.group_analytic_accounting,base.group_user"
        )
        cls.employee_user.user_id = cls.analytic_user.id
        cls.task1 = cls.env["project.task"].create(
            {
                "name": "Task One",
                "priority": "0",
                "project_id": cls.project_global.id,
                "partner_id": cls.partner_b.id,
                "user_ids": [(6, 0, cls.analytic_user.ids)],
            }
        )
        cls.env["account.analytic.line"].create(
            [
                {
                    "project_id": cls.project_global.id,
                    "task_id": cls.task1.id,
                    "name": "my first timesheet",
                    "unit_amount": 4,
                    "employee_id": cls.employee_user.id,
                },
                {
                    "project_id": cls.project_global.id,
                    "task_id": cls.task1.id,
                    "name": "my second timesheet",
                    "unit_amount": 4,
                    "employee_id": cls.employee_user.id,
                },
                {
                    "project_id": cls.project_global.id,
                    "task_id": cls.task1.id,
                    "name": "my third timesheet",
                    "unit_amount": 4,
                    "employee_id": cls.employee_user.id,
                },
            ]
        )
        cls.plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Projects Plan",
            }
        )
        cls.plan2 = cls.env["account.analytic.plan"].create(
            {
                "name": "Internal Plan",
            }
        )
        cls.analytic_account_maintenance = cls.env["account.analytic.account"].create(
            {
                "name": "Maintenance Analytic Account for Test Customer",
                "partner_id": cls.partner_b.id,
                "code": "MAINTENANCE",
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_account_sales = cls.env["account.analytic.account"].create(
            {
                "name": "Sales Analytic Account for Test Customer",
                "partner_id": cls.partner_b.id,
                "code": "SALES",
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_account_develop = cls.env["account.analytic.account"].create(
            {
                "name": "Develop Analytic Account for Test Customer",
                "partner_id": cls.partner_b.id,
                "code": "DEVELOP",
                "plan_id": cls.plan2.id,
            }
        )

        cls.so = (
            cls.env["sale.order"]
            .with_context(mail_notrack=True, mail_create_nolog=True)
            .create(
                {
                    "partner_id": cls.partner_b.id,
                    "partner_invoice_id": cls.partner_b.id,
                    "partner_shipping_id": cls.partner_b.id,
                }
            )
        )
        cls.so_line_1 = cls.env["sale.order.line"].create(
            [
                {
                    "order_id": cls.so.id,
                    "name": cls.product_delivery_timesheet1.name,
                    "product_id": cls.product_delivery_timesheet1.id,
                    "product_uom_qty": 10,
                    "price_unit": cls.product_delivery_timesheet1.list_price,
                }
            ]
        )
        cls.task1.sale_line_id = cls.so_line_1
        cls.so._create_invoices()

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    @users("test_user")
    def test_compute_account_id_01(self):
        """Test analytic account change if timesheets are invoiced."""
        plan2_fname = f"x_plan{self.plan2.id}_id"
        self.assertEqual(
            self.task1.timesheet_ids.mapped("account_id"),
            self.analytic_account_sale,
        )
        self.task1[plan2_fname] = self.analytic_account_develop
        self.task1.account_id = self.analytic_account_maintenance
        self.assertEqual(
            self.task1.timesheet_ids.mapped("account_id"),
            self.analytic_account_maintenance,
        )
        self.assertEqual(
            self.task1.timesheet_ids.mapped(plan2_fname),
            self.analytic_account_develop,
        )

    @users("test_user")
    def test_compute_account_id_02(self):
        """Test not billed analytic account lines change."""
        plan2_fname = f"x_plan{self.plan2.id}_id"
        self.assertEqual(
            self.task1.timesheet_ids.mapped("account_id"),
            self.analytic_account_sale,
        )
        timesheet_id = self.env["account.analytic.line"].create(
            [
                {
                    "project_id": self.project_global.id,
                    "task_id": self.task1.id,
                    "name": "Log additional time",
                    "unit_amount": 4,
                    "employee_id": self.employee_user.id,
                }
            ]
        )
        self.task1.account_id = self.analytic_account_maintenance
        self.task1[plan2_fname] = self.analytic_account_develop
        self.assertEqual(timesheet_id.account_id, self.analytic_account_maintenance)
        self.assertEqual(
            self.task1.timesheet_ids.mapped("account_id"),
            self.analytic_account_maintenance,
        )
        self.assertEqual(
            self.task1.timesheet_ids.mapped(plan2_fname),
            self.analytic_account_develop,
        )

    @users("test_user")
    def test_recompute_analytic_account_from_project(self):
        self.project_global.account_id = self.analytic_account_sales
        self.assertEqual(self.analytic_account_sales, self.project_global.account_id)
        self.assertEqual(self.analytic_account_sales, self.task1.account_id)
        self.assertEqual(
            self.analytic_account_sales, self.task1.timesheet_ids.mapped("account_id")
        )

    @users("test_user")
    def test_change_project_and_propagate_analytic_account_to_task(self):
        self.project_task_rate.account_id = self.analytic_account_sales
        self.task1.project_id = self.project_task_rate
        self.assertEqual(self.analytic_account_sales, self.project_task_rate.account_id)
        self.assertEqual(self.analytic_account_sales, self.task1.account_id)
        self.assertEqual(
            self.analytic_account_sales, self.task1.timesheet_ids.mapped("account_id")
        )

    @users("test_user")
    def test_change_task_project_and_propagate_to_all_timesheets(self):
        self.task1.project_id = self.project_task_rate
        project_id = self.task1.timesheet_ids.mapped("project_id")
        self.assertEqual(self.project_task_rate, project_id)
