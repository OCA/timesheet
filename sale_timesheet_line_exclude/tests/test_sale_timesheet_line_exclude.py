# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSaleTimesheetLineExclude(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.Partner = cls.env["res.partner"]
        cls.SudoPartner = cls.Partner.sudo()
        cls.Employee = cls.env["hr.employee"]
        cls.SudoEmployee = cls.Employee.sudo()
        cls.AccountAccount = cls.env["account.account"]
        cls.AccountAccountPlan = cls.env["account.analytic.plan"]
        cls.SudoAccountAccount = cls.AccountAccount.sudo()
        cls.Project = cls.env["project.project"]
        cls.SudoProject = cls.Project.sudo()
        cls.ProjectTask = cls.env["project.task"]
        cls.SudoProjectTask = cls.ProjectTask.sudo()
        cls.AccountAnalyticLine = cls.env["account.analytic.line"]
        cls.SudoAccountAnalyticLine = cls.AccountAnalyticLine.sudo()
        cls.ProductProduct = cls.env["product.product"]
        cls.SudoProductProduct = cls.ProductProduct.sudo()
        cls.SaleOrder = cls.env["sale.order"]
        cls.SudoSaleOrder = cls.SaleOrder.sudo()
        cls.SaleOrderLine = cls.env["sale.order.line"]
        cls.SudoSaleOrderLine = cls.SaleOrderLine.sudo()

        cls.analytic_plan = cls.AccountAccountPlan.create(
            {
                "name": "Plan Test",
            }
        )

        cls.analytic_account_sale = cls.env["account.analytic.account"].create(
            {
                "name": "Project for selling timesheet - AA",
                "code": "AA-20300",
                "plan_id": cls.analytic_plan.id,
            }
        )

        cls.account = cls.SudoAccountAccount.create(
            {
                "code": "TEST1",
                "name": "Sales #1",
                "reconcile": True,
                "account_type": "expense_direct_cost",
            }
        )
        cls.project = cls.SudoProject.create(
            {
                "name": "Project #1",
                "allow_timesheets": True,
                "account_id": cls.analytic_account_sale.id,
                "allow_billable": True,
            }
        )
        cls.product = cls.SudoProductProduct.create(
            {
                "name": "Service #1",
                "standard_price": 30,
                "list_price": 90,
                "type": "service",
                "invoice_policy": "delivery",
                "uom_id": cls.uom_hour.id,
                "default_code": "CODE-1",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "project_id": cls.project.id,
                "taxes_id": False,
                "property_account_income_id": cls.account.id,
            }
        )
        cls.employee = cls.SudoEmployee.create(
            {"name": "Employee #1", "hourly_cost": 42}
        )
        cls.account_payable = cls.SudoAccountAccount.create(
            {
                "code": "AP4",
                "name": "Payable #1",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        cls.account_receivable = cls.SudoAccountAccount.create(
            {
                "code": "AR1",
                "name": "Receivable #1",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.partner = cls.SudoPartner.create(
            {
                "name": "Partner #1",
                "email": "partner1@localhost",
                "property_account_payable_id": cls.account_payable.id,
                "property_account_receivable_id": cls.account_receivable.id,
            }
        )
        cls.sale_order = cls.SudoSaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.sale_order_line = cls.SudoSaleOrderLine.create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 2,
                "product_uom_id": cls.uom_hour.id,
                "price_unit": cls.product.list_price,
            }
        )
        cls.sale_order.action_confirm()
        cls.task = cls.SudoProjectTask.search(
            [("sale_line_id", "=", cls.sale_order_line.id)]
        )

    def test_create_without_exclude_from_sale_order(self):
        timesheet = self.SudoAccountAnalyticLine.create(
            {
                "project_id": self.task.project_id.id,
                "task_id": self.task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": self.employee.id,
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
            }
        )
        self.assertTrue(timesheet.so_line)
        timesheet.write({"exclude_from_sale_order": True})
        self.assertFalse(timesheet.so_line)

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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
                "account_id": self.project.account_id.id,
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
