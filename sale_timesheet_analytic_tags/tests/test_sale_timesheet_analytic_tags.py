# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleTimesheetAnalyticTags(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        self.hour_uom = self.env.ref("uom.product_uom_hour")
        self.Product = self.env["product.product"]
        self.main_company = self.env.ref("base.main_company")
        self.product_service = self.Product.create(
            {
                "name": "test",
                "type": "service",
                "uom_id": self.hour_uom.id,
                "uom_po_id": self.hour_uom.id,
                "service_tracking": "task_in_project",
            }
        )
        self.tag_test = self.env["account.analytic.tag"].create({"name": "Test"})
        self.employee_user = self.env["hr.employee"].create(
            {
                "name": "Employee User",
                "timesheet_cost": 15,
            }
        )

    def test_create_serice_so(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.user.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "name": "test1",
                            "product_uom": self.hour_uom.id,
                            "product_uom_qty": 2.0,
                            "analytic_tag_ids": [(6, 0, [self.tag_test.id])],
                        },
                    ),
                ],
            }
        )
        project_pigs = self.env["project.project"].create(
            {
                "name": "Pigs",
                "privacy_visibility": "employees",
                "alias_name": "project+pigs",
                "company_id": self.main_company.id,
            }
        )
        dummy_task = self.env["project.task"].create(
            {"name": "dummy", "project_id": project_pigs.id}
        )
        sale_order.project_id = project_pigs
        sale_order.action_confirm()
        self.assertEqual(sale_order.tasks_count, 1)
        task = sale_order.order_line[0].task_id
        with Form(
            self.env["account.analytic.line"],
            view="hr_timesheet.hr_timesheet_line_form",
        ) as line_form:
            line_form.name = "Test"
            line_form.project_id = project_pigs
            line_form.task_id = task
            line_form.unit_amount = 8.0
        line = line_form.save()
        self.assertEqual(line.tag_ids, self.tag_test)
        line.task_id = dummy_task
        self.assertFalse(line.tag_ids)
