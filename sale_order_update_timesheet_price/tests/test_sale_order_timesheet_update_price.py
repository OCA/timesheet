# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.fields import Command
from odoo.tests import Form, common


class TestSaleOrderTimesheetUpdatePrice(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "partner_id": cls.partner.id,
                "allow_billable": True,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "service_type": "timesheet",
                "service_policy": "delivered_timesheet",
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 100,
                            "price_unit": 80,
                        }
                    )
                ],
            }
        )
        cls.sale_order.action_confirm()
        cls.project.sale_line_id = (cls.sale_order.order_line[0].id,)
        cls.task = cls.env["project.task"].create(
            {
                "project_id": cls.project.id,
                "name": "Test Task",
                "sale_line_id": cls.sale_order.order_line[0].id,
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
            }
        )
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Anal Plan Test",
                # "company_id": cls.env.company.id,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Anal Account for Test",
                "plan_id": cls.analytic_plan.id,
                "code": "TEST",
                "company_id": cls.env.company.id,
            }
        )

        cls.wizard = cls.env["sale.order.unit.price.update"]

    def test_update_so_line_price_unit(self):
        initial_so_line = self.sale_order.order_line[0]
        # as there is no invoice on the so line, the update price button is not
        # displayed
        self.assertFalse(initial_so_line.price_unit_updated)
        self.assertFalse(initial_so_line.show_update_price_button)

        # create some timesheet on the task
        initial_timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "task_id": self.task.id,
                "account_id": self.project.account_id.id,
                "employee_id": self.employee.id,
                "unit_amount": 40,
            }
        )
        self.assertEqual(initial_so_line.qty_delivered, 40)

        # create an invoice
        invoice = self.sale_order._create_invoices()
        invoice.action_post()
        # as there is an invoice on the so line, the update price button is displayed
        self.assertTrue(initial_so_line.show_update_price_button)
        self.assertFalse(initial_so_line.price_unit_updated)
        self.assertEqual(self.task.sale_line_id, initial_so_line)
        self.assertEqual(self.project.sale_line_id, initial_so_line)
        # update the unit price by adding 10
        wizard = Form(self.wizard.with_context(active_id=initial_so_line.id))
        wizard.new_unit_price = initial_so_line.price_unit + 10
        wiz = wizard.save()
        wiz.action_update_unit_price()
        # check update price consequences
        self.assertTrue(initial_so_line.price_unit_updated)
        self.assertFalse(initial_so_line.show_update_price_button)
        self.assertEqual(len(self.sale_order.order_line), 2)
        updated_so_line = self.sale_order.order_line[-1]
        self.assertFalse(updated_so_line.price_unit_updated)
        self.assertFalse(updated_so_line.show_update_price_button)
        self.assertEqual(self.task.sale_line_id, updated_so_line)
        self.assertEqual(self.project.sale_line_id, updated_so_line)
        self.assertEqual(updated_so_line.price_unit, 90)
        self.assertEqual(updated_so_line.product_uom_qty, 60)

        # create some new timesheet on the task
        self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "task_id": self.task.id,
                "account_id": self.project.account_id.id,
                "employee_id": self.employee.id,
                "unit_amount": 10,
            }
        )
        self.assertEqual(updated_so_line.qty_delivered, 10)
        self.assertEqual(initial_so_line.qty_delivered, 40)  # no change

        # create some new timesheet on the project
        self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "account_id": self.project.account_id.id,
                "employee_id": self.employee.id,
                "unit_amount": 20,
            }
        )
        self.assertEqual(updated_so_line.qty_delivered, 30)

        # copy an old timesheet and verify that the so_line is updated
        self.assertEqual(initial_timesheet.so_line, initial_so_line)
        copied_timesheet = initial_timesheet.with_context(is_timesheet=1).copy()
        self.assertEqual(copied_timesheet.so_line, updated_so_line)
