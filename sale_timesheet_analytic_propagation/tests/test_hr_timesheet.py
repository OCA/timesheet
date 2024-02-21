# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)
from odoo.tests import tagged

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@tagged("-at_install", "post_install")
class HrTimesheet(TestCommonSaleTimesheet):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Timesheet = cls.env["account.analytic.line"]
        cls.task1 = cls.env["project.task"].create(
            {
                "name": "Task One",
                "priority": "0",
                "kanban_state": "normal",
                "project_id": cls.project_global.id,
                "partner_id": cls.partner_b.id,
            }
        )
        cls.Timesheet.create(
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
        cls.analytic_account_maintenance = cls.env["account.analytic.account"].create(
            {
                "name": "Maintenance Analytic Account for Test Customer",
                "partner_id": cls.partner_b.id,
                "code": "MAINTENANCE",
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
        cls.so.action_confirm()
        cls.so._create_invoices()

    def test_compute_account_id_01(self):
        """Test analytic account doesn't change if timesheets are invoiced."""
        self.assertEqual(
            set(self.task1.timesheet_ids.mapped("account_id")),
            set(self.analytic_account_sale),
        )
        self.task1.analytic_account_id = self.analytic_account_maintenance
        self.assertEqual(
            set(self.task1.timesheet_ids.mapped("account_id")),
            set(self.analytic_account_sale),
        )

    def test_compute_account_id_02(self):
        """Test only not billed analytic account lines change."""
        self.assertEqual(
            set(self.task1.timesheet_ids.mapped("account_id")),
            set(self.analytic_account_sale),
        )
        timesheet_id = self.Timesheet.create(
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
        self.task1.analytic_account_id = self.analytic_account_maintenance
        self.assertEqual(timesheet_id.account_id, self.analytic_account_maintenance)
        self.assertNotEqual(
            set(self.task1.timesheet_ids.mapped("account_id")),
            set(self.analytic_account_maintenance),
        )
