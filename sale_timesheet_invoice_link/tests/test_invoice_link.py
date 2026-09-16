# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import common


class TestInvoiceLink(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        Partner = cls.env["res.partner"]
        Employee = cls.env["hr.employee"]
        AccountAccount = cls.env["account.account"]
        AccountPlan = cls.env["account.analytic.plan"]
        Project = cls.env["project.project"]
        Product = cls.env["product.product"]
        SaleOrder = cls.env["sale.order"]
        SaleOrderLine = cls.env["sale.order.line"]

        cls.analytic_plan = AccountPlan.create({"name": "Plan Test"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test AA",
                "code": "AA-TEST",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.account_expense = AccountAccount.create(
            {
                "code": "EXP",
                "name": "Expense",
                "account_type": "expense_direct_cost",
            }
        )
        cls.account_income = AccountAccount.create(
            {
                "code": "INC",
                "name": "Income",
                "account_type": "income",
            }
        )
        cls.account_receivable = AccountAccount.create(
            {
                "code": "REC",
                "name": "Receivable",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.account_payable = AccountAccount.create(
            {
                "code": "PAY",
                "name": "Payable",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        cls.partner = Partner.create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
                "property_account_receivable_id": cls.account_receivable.id,
                "property_account_payable_id": cls.account_payable.id,
            }
        )
        cls.employee = Employee.create({"name": "Test Employee", "hourly_cost": 50})
        cls.project = Project.create(
            {
                "name": "Test Project",
                "allow_timesheets": True,
                "account_id": cls.analytic_account.id,
                "allow_billable": True,
            }
        )
        # Service product with fixed price (not timesheet delivery)
        cls.product_fixed = Product.create(
            {
                "name": "Fixed Service",
                "type": "service",
                "invoice_policy": "order",
                "service_type": "manual",
                "service_tracking": "task_global_project",
                "project_id": cls.project.id,
                "uom_id": cls.uom_hour.id,
                "standard_price": 30,
                "list_price": 100,
                "property_account_income_id": cls.account_income.id,
                "taxes_id": False,
            }
        )
        # Service product with timesheet delivery (should auto-link)
        cls.product_timesheet = Product.create(
            {
                "name": "Timesheet Service",
                "type": "service",
                "invoice_policy": "delivery",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "project_id": cls.project.id,
                "uom_id": cls.uom_hour.id,
                "standard_price": 30,
                "list_price": 100,
                "property_account_income_id": cls.account_income.id,
                "taxes_id": False,
            }
        )
        # Create SO with fixed price line
        cls.sale_order = SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
            }
        )
        cls.so_line_fixed = SaleOrderLine.create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.product_fixed.name,
                "product_id": cls.product_fixed.id,
                "product_uom_qty": 10,
                "product_uom_id": cls.uom_hour.id,
                "price_unit": cls.product_fixed.list_price,
            }
        )
        cls.so_line_timesheet = SaleOrderLine.create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.product_timesheet.name,
                "product_id": cls.product_timesheet.id,
                "product_uom_qty": 5,
                "product_uom_id": cls.uom_hour.id,
                "price_unit": cls.product_timesheet.list_price,
            }
        )
        cls.sale_order.action_confirm()
        # Get the task created for the fixed price line
        cls.task_fixed = cls.env["project.task"].search(
            [("sale_line_id", "=", cls.so_line_fixed.id)]
        )
        cls.task_timesheet = cls.env["project.task"].search(
            [("sale_line_id", "=", cls.so_line_timesheet.id)]
        )

    def _create_timesheet(self, task, unit_amount=1.0):
        return self.env["account.analytic.line"].create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Test timesheet entry",
                "unit_amount": unit_amount,
                "employee_id": self.employee.id,
                "account_id": self.project.account_id.id,
            }
        )

    def test_pending_timesheets_fixed_price(self):
        """Timesheets on fixed-price SO lines should appear as pending."""
        ts = self._create_timesheet(self.task_fixed)
        self.assertEqual(ts.timesheet_invoice_type, "billable_fixed")
        # Create invoice manually
        invoice = self.sale_order._create_invoices()
        self.assertTrue(invoice)
        self.assertEqual(invoice.timesheet_pending_count, 1)
        self.assertIn(ts, invoice.timesheet_pending_ids)

    def test_pending_timesheets_timesheet_delivery(self):
        """Timesheets on timesheet-delivery SO lines should NOT be pending
        (they get auto-linked by standard flow)."""
        ts = self._create_timesheet(self.task_timesheet)
        self.assertEqual(ts.timesheet_invoice_type, "billable_time")
        invoice = self.sale_order._create_invoices()
        self.assertTrue(invoice)
        # The timesheet should be auto-linked, so not pending
        self.assertEqual(invoice.timesheet_pending_count, 0)
        self.assertTrue(ts.timesheet_invoice_id)

    def test_action_link_timesheets(self):
        """Link All should set timesheet_invoice_id on all pending."""
        ts = self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        self.assertEqual(invoice.timesheet_pending_count, 1)
        invoice.action_link_timesheets()
        self.assertTrue(ts.timesheet_invoice_id)
        self.assertEqual(ts.timesheet_invoice_id, invoice)
        self.assertTrue(invoice.timesheet_alert_dismissed)

    def test_action_dismiss_timesheet_alert(self):
        """Dismiss should set timesheet_alert_dismissed."""
        self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        self.assertFalse(invoice.timesheet_alert_dismissed)
        invoice.action_dismiss_timesheet_alert()
        self.assertTrue(invoice.timesheet_alert_dismissed)

    def test_no_pending_when_all_linked(self):
        """No pending timesheets when all are already linked."""
        self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        invoice.action_link_timesheets()
        self.env.invalidate_all()
        self.assertEqual(invoice.timesheet_pending_count, 0)

    def test_pending_count_multiple_timesheets(self):
        """Multiple timesheets should all be counted as pending."""
        self._create_timesheet(self.task_fixed, 1.0)
        self._create_timesheet(self.task_fixed, 2.0)
        self._create_timesheet(self.task_fixed, 3.0)
        invoice = self.sale_order._create_invoices()
        self.assertEqual(invoice.timesheet_pending_count, 3)

    def test_no_pending_for_non_out_invoice(self):
        """Vendor bills should not have pending timesheets."""
        self._create_timesheet(self.task_fixed)
        invoice = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        self.assertEqual(invoice.timesheet_pending_count, 0)

    def test_action_select_timesheets(self):
        """Select Manually should return an action with the right domain."""
        self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        action = invoice.action_select_timesheets()
        self.assertEqual(action["res_model"], "account.analytic.line")
        self.assertEqual(action["view_mode"], "list,form")
        self.assertIn("id", action["domain"][0])

    def test_reset_to_draft_after_dismiss(self):
        """Reset to draft after dismiss should show alert again."""
        self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        invoice.action_dismiss_timesheet_alert()
        self.assertTrue(invoice.timesheet_alert_dismissed)
        invoice.action_post()
        invoice.button_draft()
        self.assertFalse(invoice.timesheet_alert_dismissed)
        self.assertEqual(invoice.timesheet_pending_count, 1)

    def test_reset_to_draft_after_link_all(self):
        """Reset to draft after link all: alert reappears but no pending
        (timesheet is still linked to the draft invoice)."""
        self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        invoice.action_link_timesheets()
        self.env.invalidate_all()
        self.assertTrue(invoice.timesheet_alert_dismissed)
        self.assertEqual(invoice.timesheet_pending_count, 0)
        invoice.action_post()
        invoice.button_draft()
        self.assertFalse(invoice.timesheet_alert_dismissed)
        self.assertEqual(invoice.timesheet_pending_count, 0)

    def test_reset_to_draft_no_pending(self):
        """Reset to draft without pending timesheets should not show alert."""
        invoice = self.sale_order._create_invoices()
        self.assertEqual(invoice.timesheet_pending_count, 0)
        invoice.action_post()
        invoice.button_draft()
        self.assertFalse(invoice.timesheet_alert_dismissed)
        self.assertEqual(invoice.timesheet_pending_count, 0)

    def test_reset_to_draft_with_new_timesheet_after_link_all(self):
        """New timesheet after link all + post should appear pending on draft."""
        self._create_timesheet(self.task_fixed)
        invoice = self.sale_order._create_invoices()
        invoice.action_link_timesheets()
        self.env.invalidate_all()
        self.assertEqual(invoice.timesheet_pending_count, 0)
        invoice.action_post()
        self._create_timesheet(self.task_fixed)
        invoice.button_draft()
        self.assertFalse(invoice.timesheet_alert_dismissed)
        self.assertEqual(invoice.timesheet_pending_count, 1)
