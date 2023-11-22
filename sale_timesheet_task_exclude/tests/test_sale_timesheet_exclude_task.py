# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestSaleTimesheetExcludeTask(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.uom_hour = self.env.ref("uom.product_uom_hour")
        self.Partner = self.env["res.partner"]
        self.SudoPartner = self.Partner.sudo()
        self.Employee = self.env["hr.employee"]
        self.SudoEmployee = self.Employee.sudo()
        self.AccountAccount = self.env["account.account"]
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
        self.analytic_plan = self.env["account.analytic.plan"].create(
            {
                "name": "Plan Test",
                "company_id": self.env.company.id,
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

    def test_exclude_from_sale_order(self):
        account = self.SudoAccountAccount.create(
            {
                "code": "TEST1",
                "name": "Sales #1",
                "reconcile": True,
                "account_type": "expense_direct_cost",
            }
        )
        project = self.SudoProject.create(
            {
                "name": "Project #1",
                "allow_timesheets": True,
                "allow_billable": True,
                "analytic_account_id": self.analytic_account_sale.id,
            }
        )
        product = self.SudoProductProduct.create(
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
        employee = self.SudoEmployee.create({"name": "Employee #1", "hourly_cost": 42})
        account_payable = self.SudoAccountAccount.create(
            {
                "code": "AP1",
                "name": "Payable #1",
                "reconcile": True,
                "account_type": "liability_payable",
            }
        )
        account_receivable = self.SudoAccountAccount.create(
            {
                "code": "AR1",
                "name": "Receivable #1",
                "reconcile": True,
                "account_type": "asset_receivable",
            }
        )
        partner = self.SudoPartner.create(
            {
                "name": "Partner #1",
                "email": "partner1@localhost",
                "property_account_payable_id": account_payable.id,
                "property_account_receivable_id": account_receivable.id,
            }
        )
        sale_order = self.SudoSaleOrder.create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
            }
        )
        sale_order_line = self.SudoSaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 2,
                "product_uom": self.uom_hour.id,
                "price_unit": product.list_price,
            }
        )
        sale_order.action_confirm()
        task = self.SudoProjectTask.search([("sale_line_id", "=", sale_order_line.id)])
        timesheet = self.SudoAccountAnalyticLine.create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Entry #1",
                "unit_amount": 1,
                "employee_id": employee.id,
                "account_id": project.analytic_account_id.id,
            }
        )
        task.exclude_from_sale_order = True
        task.allow_billable = False
        self.assertFalse(timesheet.so_line)
        task.write({"exclude_from_sale_order": False, "allow_billable": True})
        self.assertTrue(timesheet.so_line)

        payment = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                **{
                    "active_model": "sale.order",
                    "active_ids": [sale_order.id],
                    "active_id": sale_order.id,
                }
            )
            .create({"advance_payment_method": "delivered"})
        )
        payment.create_invoices()

        task.exclude_from_sale_order = True
        self.assertTrue(timesheet.so_line)
