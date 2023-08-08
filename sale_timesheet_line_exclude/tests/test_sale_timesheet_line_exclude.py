# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSaleTimesheetLineExclude(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.uom_hour = self.env.ref("uom.product_uom_hour")
        self.Partner = self.env["res.partner"]
        self.SudoPartner = self.Partner.sudo()
        self.Employee = self.env["hr.employee"]
        self.SudoEmployee = self.Employee.sudo()
        self.AccountAccount = self.env["account.account"]
        self.AccountAccountPlan = self.env["account.analytic.plan"]
        self.SudoAccountAccount = self.AccountAccount.sudo()
        self.Project = self.env["project.project"]
        self.SudoProject = self.Project.sudo()
        self.ProjectTask = self.env["project.task"]
        self.SudoProjectTask = self.ProjectTask.sudo()
        self.AccountAnalyticLine = self.env["account.analytic.line"]
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.ProductProduct = self.env["product.product"]
        self.SudoProductProduct = self.ProductProduct.sudo()
        self.SaleOrder = self.env["sale.order"]
        self.SudoSaleOrder = self.SaleOrder.sudo()
        self.SaleOrderLine = self.env["sale.order.line"]
        self.SudoSaleOrderLine = self.SaleOrderLine.sudo()
        self.ProjectCreateSaleOrder = self.env["project.create.sale.order"]

        self.analytic_plan = self.AccountAccountPlan.create(
            {
                "name": "Plan Test",
                "company_id": False,
            }
        )

        self.analytic_account_sale = self.env["account.analytic.account"].create(
            {
                "name": "Project for selling timesheet - AA",
                "code": "AA-20300",
                "company_id": self.env.company.id,
                "plan_id": self.analytic_plan.id,
            }
        )

        self.account = self.SudoAccountAccount.create(
            {
                "code": "TEST1",
                "name": "Sales #1",
                "reconcile": True,
                "account_type": "expense_direct_cost",
            }
        )
        self.project = self.SudoProject.create(
            {
                "name": "Project #1",
                "allow_timesheets": True,
                "analytic_account_id": self.analytic_account_sale.id,
                "allow_billable": True,
            }
        )
        self.product = self.SudoProductProduct.create(
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
                "project_id": self.project.id,
                "taxes_id": False,
                "property_account_income_id": self.account.id,
            }
        )
        self.employee = self.SudoEmployee.create(
            {"name": "Employee #1", "hourly_cost": 42}
        )
        self.account_payable = self.SudoAccountAccount.create(
            {
                "code": "AP4",
                "name": "Payable #1",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        self.account_receivable = self.SudoAccountAccount.create(
            {
                "code": "AR1",
                "name": "Receivable #1",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        self.partner = self.SudoPartner.create(
            {
                "name": "Partner #1",
                "email": "partner1@localhost",
                "property_account_payable_id": self.account_payable.id,
                "property_account_receivable_id": self.account_receivable.id,
            }
        )
        self.sale_order = self.SudoSaleOrder.create(
            {
                "partner_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
            }
        )
        self.sale_order_line = self.SudoSaleOrderLine.create(
            {
                "order_id": self.sale_order.id,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 2,
                "product_uom": self.uom_hour.id,
                "price_unit": self.product.list_price,
            }
        )
        self.sale_order.action_confirm()
        self.task = self.SudoProjectTask.search(
            [("sale_line_id", "=", self.sale_order_line.id)]
        )

    def test_create_without_exclude_from_sale_order(self):
        timesheet = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "account_id": self.project.analytic_account_id.id,
            }
        )
        self.assertEqual(timesheet.timesheet_invoice_type, "billable_time")
        self.assertEqual(self.sale_order_line.qty_delivered, 1)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 1)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

    def test_create_with_exclude_from_sale_order(self):
        timesheet = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "exclude_from_sale_order": True,
                "account_id": self.project.analytic_account_id.id,
            }
        )
        self.assertEqual(timesheet.timesheet_invoice_type, "non_billable")
        self.assertEqual(self.sale_order_line.qty_delivered, 0)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 0)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

    def test_write_exclude_from_sale_order(self):
        timesheet = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "exclude_from_sale_order": False,
                "account_id": self.project.analytic_account_id.id,
            }
        )
        timesheet.write({"exclude_from_sale_order": True})

        self.assertEqual(timesheet.timesheet_invoice_type, "non_billable")
        self.assertEqual(self.sale_order_line.qty_delivered, 0)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 0)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

    def test_write_remove_exclude_from_sale_order(self):
        timesheet = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "exclude_from_sale_order": True,
                "account_id": self.project.analytic_account_id.id,
            }
        )
        timesheet.write({"exclude_from_sale_order": False})

        self.assertTrue(timesheet.so_line)
        self.assertEqual(timesheet.timesheet_invoice_type, "billable_time")
        self.assertEqual(self.sale_order_line.qty_delivered, 1)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 1)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

    def test_create_invoice(self):
        timesheet1 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "account_id": self.project.analytic_account_id.id,
            }
        )

        timesheet2 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "exclude_from_sale_order": True,
                "account_id": self.project.analytic_account_id.id,
            }
        )

        self.assertEqual(timesheet1.timesheet_invoice_type, "billable_time")
        self.assertEqual(timesheet2.timesheet_invoice_type, "non_billable")
        self.assertEqual(self.sale_order_line.qty_delivered, 1)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 1)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)
        self.sale_order._create_invoices()
        self.assertTrue(timesheet1.timesheet_invoice_id)
        self.assertEqual(self.sale_order_line.qty_delivered, 1)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 0)
        self.assertEqual(self.sale_order_line.qty_invoiced, 1)

    def test_write_invoiced(self):
        timesheet1 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "account_id": self.project.analytic_account_id.id,
            }
        )

        timesheet2 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "exclude_from_sale_order": True,
                "account_id": self.project.analytic_account_id.id,
            }
        )

        self.assertEqual(timesheet1.timesheet_invoice_type, "billable_time")
        self.assertEqual(timesheet2.timesheet_invoice_type, "non_billable")
        self.assertEqual(self.sale_order_line.qty_delivered, 1)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 1)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)
        self.sale_order._create_invoices()
        self.assertTrue(timesheet1.timesheet_invoice_id)
        self.assertEqual(self.sale_order_line.qty_delivered, 1)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 0)
        self.assertEqual(self.sale_order_line.qty_invoiced, 1)

        with self.assertRaises(ValidationError):
            timesheet1.write({"exclude_from_sale_order": True})

    def test_1(self):
        timesheet1 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "account_id": self.project.analytic_account_id.id,
            }
        )
        timesheet2 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-2",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "exclude_from_sale_order": False,
                "account_id": self.project.analytic_account_id.id,
            }
        )

        self.assertEqual(timesheet1.timesheet_invoice_type, "billable_time")
        self.assertEqual(timesheet2.timesheet_invoice_type, "billable_time")
        self.assertEqual(self.sale_order_line.qty_delivered, 2)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 2)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

        timesheet3 = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-3",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "account_id": self.project.analytic_account_id.id,
            }
        )
        self.assertEqual(timesheet3.timesheet_invoice_type, "billable_time")
        self.assertTrue(timesheet3.so_line)
        self.assertEqual(self.sale_order_line.qty_delivered, 3)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 3)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

        self.assertEqual(timesheet1.timesheet_invoice_type, "billable_time")
        self.assertTrue(timesheet1.so_line)

        timesheet2.write({"exclude_from_sale_order": True})
        self.assertEqual(timesheet2.timesheet_invoice_type, "non_billable")
        self.assertFalse(timesheet2.so_line)

        self.assertEqual(self.sale_order_line.qty_delivered, 2)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 2)
        self.assertEqual(self.sale_order_line.qty_invoiced, 0)

        self.assertFalse(timesheet1.timesheet_invoice_id)
        self.sale_order._create_invoices()
        self.assertTrue(timesheet1.timesheet_invoice_id)
        self.assertEqual(self.sale_order_line.qty_delivered, 2)
        self.assertEqual(self.sale_order_line.qty_to_invoice, 0)
        self.assertEqual(self.sale_order_line.qty_invoiced, 2)
        with self.assertRaises(ValidationError):
            timesheet1.write({"exclude_from_sale_order": True})
