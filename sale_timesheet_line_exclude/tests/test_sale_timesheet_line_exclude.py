# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSaleTimesheetLineExclude(common.TransactionCase):
    def setUp(self):
        super(TestSaleTimesheetLineExclude, self).setUp()

        self.uom_hour = self.env.ref("uom.product_uom_hour")
        self.user_type_payable = self.env.ref("account.data_account_type_payable")
        self.user_type_receivable = self.env.ref("account.data_account_type_receivable")
        self.user_type_revenue = self.env.ref("account.data_account_type_revenue")
        self.Partner = self.env["res.partner"]
        self.Employee = self.env["hr.employee"]
        self.AccountAccount = self.env["account.account"]
        self.Project = self.env["project.project"]
        self.ProjectTask = self.env["project.task"]
        self.AccountAnalyticLine = self.env["account.analytic.line"]
        self.ProductProduct = self.env["product.product"]
        self.SaleOrder = self.env["sale.order"]
        self.SaleOrderLine = self.env["sale.order.line"]
        self.ProjectCreateSaleOrder = self.env["project.create.sale.order"]

    def test_1(self):
        account = self.AccountAccount.create(
            {
                "code": "TEST-1",
                "name": "Sales #1",
                "reconcile": True,
                "user_type_id": self.user_type_revenue.id,
            }
        )
        project = self.Project.create(
            {"name": "Project #1", "allow_timesheets": True, "allow_billable": True}
        )
        product = self.ProductProduct.create(
            {
                "name": "Service #1",
                "standard_price": 30,
                "list_price": 90,
                "type": "service",
                "invoice_policy": "delivery",
                "uom_id": self.uom_hour.id,
                "uom_po_id": self.uom_hour.id,
                "default_code": "CODE-1",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "project_id": project.id,
                "taxes_id": False,
                "property_account_income_id": account.id,
            }
        )
        employee = self.Employee.create({"name": "Employee #1", "timesheet_cost": 42})
        account_payable = self.AccountAccount.create(
            {
                "code": "AP4",
                "name": "Payable #1",
                "user_type_id": self.user_type_payable.id,
                "reconcile": True,
            }
        )
        account_receivable = self.AccountAccount.create(
            {
                "code": "AR1",
                "name": "Receivable #1",
                "user_type_id": self.user_type_receivable.id,
                "reconcile": True,
            }
        )
        partner = self.Partner.create(
            {
                "name": "Partner #1",
                "email": "partner1@localhost",
                "property_account_payable_id": account_payable.id,
                "property_account_receivable_id": account_receivable.id,
            }
        )
        sale_order = self.SaleOrder.create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
            }
        )
        sale_order_line = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 0,
                "product_uom": self.uom_hour.id,
                "price_unit": product.list_price,
            }
        )
        sale_order.action_confirm()
        task = self.ProjectTask.search([("sale_line_id", "=", sale_order_line.id)])
        timesheet1 = self.AccountAnalyticLine.create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": employee.id,
            }
        )
        timesheet2 = self.AccountAnalyticLine.create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Entry #1-2",
                "unit_amount": 1,
                "employee_id": employee.id,
                "exclude_from_sale_order": False,
            }
        )

        self.assertEqual(timesheet1.timesheet_invoice_type, "billable_time")
        self.assertEqual(timesheet2.timesheet_invoice_type, "billable_time")
        self.assertEqual(sale_order_line.qty_delivered, 2)
        self.assertEqual(sale_order_line.qty_to_invoice, 2)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        timesheet3 = self.AccountAnalyticLine.create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Entry #1-3",
                "unit_amount": 1,
                "employee_id": employee.id,
            }
        )
        self.assertEqual(timesheet3.timesheet_invoice_type, "billable_time")
        self.assertEqual(sale_order_line.qty_delivered, 3)
        self.assertEqual(sale_order_line.qty_to_invoice, 3)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        timesheet1._onchange_task_id_employee_id()
        self.assertEqual(timesheet1.timesheet_invoice_type, "billable_time")
        self.assertTrue(timesheet1.so_line)

        timesheet2.write({"exclude_from_sale_order": True})
        timesheet2._onchange_task_id_employee_id()
        self.assertEqual(timesheet2.timesheet_invoice_type, "non_billable")
        self.assertFalse(timesheet2.so_line)

        timesheet3._onchange_exclude_from_sale_order()
        self.assertEqual(timesheet3.timesheet_invoice_type, "billable_time")
        self.assertTrue(timesheet3.so_line)

        self.assertEqual(sale_order_line.qty_delivered, 2)
        self.assertEqual(sale_order_line.qty_to_invoice, 2)
        self.assertEqual(sale_order_line.qty_invoiced, 0)

        self.assertFalse(timesheet1.timesheet_invoice_id)
        sale_order._create_invoices()
        self.assertTrue(timesheet1.timesheet_invoice_id)
        self.assertEqual(sale_order_line.qty_delivered, 2)
        self.assertEqual(sale_order_line.qty_to_invoice, 0)
        self.assertEqual(sale_order_line.qty_invoiced, 2)
        with self.assertRaises(ValidationError):
            timesheet1.write({"exclude_from_sale_order": True})
