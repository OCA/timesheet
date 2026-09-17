# Copyright 2026 Innovara Ltd - Manuel Fombuena
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleTimesheetCostsRevenues(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env["sale.timesheet.costs.revenues"]
        cls.hour_uom = cls.env.ref("uom.product_uom_hour")
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Test Worker", "hourly_cost": 60.0}
        )
        # Service product billed on delivered timesheets, creating its own
        # project + task when the sale order is confirmed.
        cls.product = cls.env["product.product"].create(
            {
                "name": "Consulting",
                "type": "service",
                "invoice_policy": "delivery",
                "service_type": "timesheet",
                "service_tracking": "task_in_project",
                "list_price": 100.0,
                "standard_price": 60.0,
                "uom_id": cls.hour_uom.id,
                "uom_po_id": cls.hour_uom.id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 10.0})
                ],
            }
        )
        cls.sale_order.action_confirm()
        cls.so_line = cls.sale_order.order_line
        cls.project = cls.so_line.project_id
        cls.task = cls.so_line.task_id
        cls.timesheet = cls.env["account.analytic.line"].create(
            {
                "name": "Work done",
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "employee_id": cls.employee.id,
                "unit_amount": 4.0,
            }
        )

    def _rows(self):
        # The report is a SQL view over account_analytic_line; searching it
        # does not flush that table, so push pending ORM writes (e.g. the
        # timesheet's invoice link) to the database before querying.
        self.env.flush_all()
        return self.report.search([("project_id", "=", self.project.id)])

    def test_duration_matches_logged_hours(self):
        self.assertEqual(sum(self._rows().mapped("timesheet_duration")), 4.0)

    def test_cost_is_negative_and_proportional(self):
        # 4 hours * 60.0 hourly cost, stored negative
        self.assertAlmostEqual(
            sum(self._rows().mapped("timesheet_cost")), -240.0, places=2
        )

    def test_amount_to_invoice_before_invoicing(self):
        # 4 logged hours * 100.0 sale price, nothing invoiced yet
        rows = self._rows()
        self.assertAlmostEqual(sum(rows.mapped("amount_to_invoice")), 400.0, places=2)
        self.assertEqual(sum(rows.mapped("amount_invoiced")), 0.0)

    def test_amount_moves_to_invoiced_after_invoicing(self):
        # The timesheet is delivered and linked to the sale order line (the
        # "before" test already proves the link, since the report only values
        # timesheets that have a so_line).
        self.assertEqual(self.so_line.qty_delivered, 4.0)
        # Invoice the delivered timesheets through the sales advance-payment
        # wizard ("regular invoice"): the supported path that stamps each
        # invoiced timesheet with its invoice (timesheet_invoice_id).
        self.env["sale.advance.payment.inv"].with_context(
            active_ids=self.sale_order.ids,
            active_model="sale.order",
        ).create({"advance_payment_method": "delivered"}).create_invoices()
        self.sale_order.invoice_ids.action_post()
        # Odoo should now have linked the timesheet to the invoice; this is
        # what flips it from "to invoice" to "invoiced" in the report.
        self.assertTrue(self.timesheet.timesheet_invoice_id)
        rows = self._rows()
        self.assertEqual(sum(rows.mapped("amount_to_invoice")), 0.0)
        self.assertAlmostEqual(sum(rows.mapped("amount_invoiced")), 400.0, places=2)

    def test_non_timesheet_line_is_excluded(self):
        # An analytic line with no project must not surface in the report.
        plan = self.env["account.analytic.plan"].create({"name": "Test Plan"})
        account = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account", "plan_id": plan.id}
        )
        self.env["account.analytic.line"].create(
            {"name": "Misc cost", "account_id": account.id, "amount": -50.0}
        )
        self.assertFalse(self.report.search([("account_id", "=", account.id)]))
