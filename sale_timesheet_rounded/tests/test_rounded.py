# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import odoo
from odoo import fields

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@odoo.tests.tagged("post_install", "-at_install")
class TestRounded(TestCommonSaleTimesheet):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.sale_order = cls.env["sale.order"].create(
            {
                "analytic_account_id": cls.project_global.analytic_account_id.id,
                "partner_id": cls.partner_a.id,
                "partner_invoice_id": cls.partner_a.id,
                "partner_shipping_id": cls.partner_a.id,
            }
        )
        sale_order_line = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.product_delivery_timesheet2.name,
                "product_id": cls.product_delivery_timesheet2.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_delivery_timesheet2.uom_id.id,
                "price_unit": cls.product_delivery_timesheet2.list_price,
            }
        )
        sale_order_line.product_id_change()
        cls.sale_order.action_confirm()
        cls.project_global.write(
            {
                "timesheet_rounding_unit": 0.25,
                "timesheet_rounding_method": "UP",
                "timesheet_rounding_factor": 200,
            }
        )
        cls.product_expense = cls.env["product.product"].create(
            {
                "name": "Service delivered, EXPENSE",
                "expense_policy": "cost",
                "standard_price": 30,
                "list_price": 90,
                "type": "service",
                "invoice_policy": "order",
                "uom_id": cls.product_delivery_timesheet2.uom_id.id,
                "uom_po_id": cls.product_delivery_timesheet2.uom_id.id,
            }
        )
        cls.avg_analytic_account = cls.env["account.analytic.account"].create(
            {"name": "AVG account"}
        )

    def create_analytic_line(self, **kw):
        task = self.sale_order.tasks_ids[0]
        values = {
            "project_id": self.project_global.id,
            "task_id": task.id,
            "name": "Rounded test line",
            "date": fields.Date.today(),
            "unit_amount": 0,
            "product_id": self.product_delivery_timesheet2.id,
            "employee_id": self.employee_user.id,
        }
        values.update(kw)
        return self.env["account.analytic.line"].create(values)

    def test_analytic_line_init_no_rounding(self):
        lines = self.env["account.analytic.line"].search([])
        for line in lines:
            self.assertEqual(line.unit_amount_rounded, line.unit_amount)

    def test_analytic_line_create_no_rounding(self):
        self.project_global.write({"timesheet_rounding_method": "NO"})
        # no rounding enabled
        line = self.create_analytic_line(unit_amount=1)
        self.assertEqual(line.unit_amount, 1.0)
        self.assertEqual(line.unit_amount_rounded, line.unit_amount)

    def test_analytic_line_create(self):
        line = self.create_analytic_line(unit_amount=1)
        self.assertEqual(line.unit_amount_rounded, 2.0)
        line = self.create_analytic_line(unit_amount=1, unit_amount_rounded=0)
        self.assertEqual(line.unit_amount_rounded, 0.0)

    def test_analytic_line_create_and_update_amount_rounded(self):
        line = self.create_analytic_line(unit_amount=2)
        self.assertEqual(line.unit_amount_rounded, 4.0)
        line.write({"unit_amount_rounded": 5.0})
        self.assertEqual(line.unit_amount_rounded, 5.0)
        line.write({"unit_amount_rounded": 0.0})
        self.assertEqual(line.unit_amount_rounded, 0.0)

    def test_analytic_line_create_and_update_amount(self):
        line = self.create_analytic_line(unit_amount=2)
        self.assertEqual(line.unit_amount_rounded, 4.0)
        line.unit_amount = 5.0
        self.assertEqual(line.unit_amount_rounded, 10.0)

    def test_analytic_line_read_group_override(self):
        # Test of the read group with an without timesheet_rounding context
        # without context the unit_amount should be the initial
        # with the context the value of unit_amount should be replaced by the
        # unit_amount_rounded
        line = self.env["account.analytic.line"]
        self.create_analytic_line(unit_amount=1)
        domain = [("project_id", "=", self.project_global.id)]
        fields_list = ["so_line", "unit_amount", "product_uom_id"]
        groupby = ["product_uom_id", "so_line"]

        data_ctx_f = line.read_group(
            domain,
            fields_list,
            groupby,
        )
        self.assertEqual(data_ctx_f[0]["unit_amount"], 1.0)

        data_ctx_t = line.with_context(timesheet_rounding=True).read_group(
            domain,
            fields_list,
            groupby,
        )
        self.assertEqual(data_ctx_t[0]["unit_amount"], 2.0)

        self.create_analytic_line(unit_amount=1.1)
        data_ctx_f = line.with_context(timesheet_rounding=False).read_group(
            domain,
            fields_list,
            groupby,
        )
        self.assertEqual(data_ctx_f[0]["unit_amount"], 2.1)

        data_ctx_f = line.with_context(timesheet_rounding=True).read_group(
            domain,
            fields_list,
            groupby,
        )
        self.assertEqual(data_ctx_f[0]["unit_amount"], 4.25)

    def test_analytic_line_read_override(self):
        # Cases for not rounding:
        # * not linked to project -> no impact
        # * is an expense -> no impact
        # * ctx key for rounding is set to false -> no impact
        # In all the other cases we check that unit amount is rounded.
        load = "_classic_read"
        fields = None

        # context = False + project_id - product_expense
        line = self.create_analytic_line(unit_amount=1)
        unit_amount_ret = line.read(fields, load)[0]["unit_amount"]
        self.assertEqual(unit_amount_ret, 1)

        # context = True - project - product_expense
        line = self.create_analytic_line(
            unit_amount=1, project_id=False, account_id=self.avg_analytic_account.id
        )
        unit_amount_ret = line.with_context(timesheet_rounding=True).read(fields, load)[
            0
        ]["unit_amount"]
        self.assertEqual(unit_amount_ret, 1)

        # context = True + project_id + product_expense
        line = self.create_analytic_line(
            unit_amount=1, product_id=self.product_expense.id
        )
        unit_amount_ret = line.with_context(timesheet_rounding=True).read(fields, load)[
            0
        ]["unit_amount"]
        self.assertEqual(unit_amount_ret, 2)

        # context = True + project_id - product_expense
        line = self.create_analytic_line(unit_amount=1)
        unit_amount_ret = line.with_context(timesheet_rounding=True).read(fields, load)[
            0
        ]["unit_amount"]
        self.assertEqual(unit_amount_ret, 2)

    def test_sale_order_qty_1(self):
        # amount=1 -> should be rounded to 2 by the invoicing_factor
        self.create_analytic_line(unit_amount=1)
        self.assertAlmostEqual(self.sale_order.order_line.qty_delivered, 2.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_to_invoice, 2.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_invoiced, 0)

    def test_sale_order_qty_2(self):
        # force amount_rounded=4
        self.create_analytic_line(unit_amount=1, unit_amount_rounded=4)
        self.assertAlmostEqual(self.sale_order.order_line.qty_delivered, 4.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_to_invoice, 4.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_invoiced, 0)

    def test_sale_order_qty_3(self):
        # amount=0.9
        # should be rounded to 2 by the invoicing_factor with the project
        # timesheet_rounding_unit: 0.25
        # timesheet_rounding_method: 'UP'
        # timesheet_rounding_factor: 200
        self.create_analytic_line(unit_amount=0.9)
        self.assertAlmostEqual(self.sale_order.order_line.qty_delivered, 2.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_to_invoice, 2.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_invoiced, 0)

    def test_sale_order_qty_4(self):
        # amount=0.9
        # should be rounded to 2 by the invoicing_factor with the project
        # timesheet_rounding_unit: 0.25
        # timesheet_rounding_method: 'UP'
        # timesheet_rounding_factor: 200
        self.project_global.timesheet_rounding_factor = 400
        self.create_analytic_line(unit_amount=1.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_delivered, 4.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_to_invoice, 4.0)
        self.assertAlmostEqual(self.sale_order.order_line.qty_invoiced, 0)

    def test_calc_rounded_amount_method(self):
        aal = self.env["account.analytic.line"]
        rounding_unit = 0.25
        rounding_method = "UP"
        factor = 200
        amount = 1
        self.assertEqual(
            aal._calc_rounded_amount(rounding_unit, rounding_method, factor, amount), 2
        )

        rounding_unit = 0.0
        rounding_method = "UP"
        factor = 200
        amount = 1
        self.assertEqual(
            aal._calc_rounded_amount(rounding_unit, rounding_method, factor, amount), 2
        )

        rounding_unit = 0.25
        rounding_method = "UP"
        factor = 100
        amount = 1.0
        self.assertEqual(
            aal._calc_rounded_amount(rounding_unit, rounding_method, factor, amount), 1
        )

        rounding_unit = 0.25
        rounding_method = "UP"
        factor = 200
        amount = 0.9
        self.assertEqual(
            aal._calc_rounded_amount(rounding_unit, rounding_method, factor, amount), 2
        )

        rounding_unit = 1.0
        rounding_method = "UP"
        factor = 200
        amount = 0.6
        self.assertEqual(
            aal._calc_rounded_amount(rounding_unit, rounding_method, factor, amount), 2
        )

        rounding_unit = 0.25
        rounding_method = "HALF_UP"
        factor = 200
        amount = 1.01
        self.assertEqual(
            aal._calc_rounded_amount(rounding_unit, rounding_method, factor, amount), 2
        )

    def test_post_invoice_with_rounded_amount_unchanged(self):
        """Posting an invoice MUST NOT recompute rounded amount unit.
        - invoicing the SO should not recompute and update the
        unit_amount_rounded
        - the invoiced qty should be the same as the aal.unit_amount_rounded
        """
        unit_amount_rounded = 111
        analytic_line = self.create_analytic_line(unit_amount=10)
        analytic_line.unit_amount_rounded = unit_amount_rounded
        account_move = self.sale_order._create_invoices()
        prd_ts_id = self.product_delivery_timesheet2
        account_move._post()
        # the unit_amount_rounded is not changed
        self.assertEqual(analytic_line.unit_amount_rounded, unit_amount_rounded)
        # the invoiced qty remains the same
        inv_line = account_move.line_ids.filtered(lambda l: l.product_id == prd_ts_id)
        self.assertEqual(inv_line.quantity, unit_amount_rounded)

    def test_draft_invoice_with_rounded_amount_unchanged(self):
        """Drafting an invoice MUST NOT recompute rounded amount unit.
        - invoicing the SO should not recompute and update the
        unit_amount_rounded
        - the invoiced qty should be the same as the aal.unit_amount_rounded
        """
        unit_amount_rounded = 0.12
        analytic_line = self.create_analytic_line(unit_amount=10)
        analytic_line.unit_amount_rounded = unit_amount_rounded
        account_move = self.sale_order._create_invoices()
        prd_ts_id = self.product_delivery_timesheet2
        account_move.button_draft()
        # the unit_amount_rounded is not changed
        self.assertEqual(analytic_line.unit_amount_rounded, unit_amount_rounded)
        # the invoiced qty remains the same
        inv_line = account_move.line_ids.filtered(lambda l: l.product_id == prd_ts_id)
        self.assertEqual(inv_line.quantity, unit_amount_rounded)

    def test_cancel_invoice_with_rounded_amount_unchanged(self):
        """Cancelling an invoice MUST NOT recompute rounded amount unit.
        - invoicing the SO should not recompute and update the
        unit_amount_rounded
        - the invoiced qty should be the same as the aal.unit_amount_rounded
        """
        unit_amount_rounded_total = 15
        analytic_line_1 = self.create_analytic_line(unit_amount=10)
        analytic_line_2 = self.create_analytic_line(unit_amount=10)
        analytic_line_1.unit_amount_rounded = unit_amount_rounded_total
        analytic_line_2.unit_amount_rounded = 0
        account_move = self.sale_order._create_invoices()
        prd_ts_id = self.product_delivery_timesheet2
        account_move.button_cancel()
        # the unit_amount_rounded is not changed
        self.assertEqual(analytic_line_1.unit_amount_rounded, unit_amount_rounded_total)
        self.assertEqual(analytic_line_2.unit_amount_rounded, 0)
        # the invoiced qty remains the same
        inv_line = account_move.line_ids.filtered(lambda l: l.product_id == prd_ts_id)
        self.assertEqual(inv_line.quantity, unit_amount_rounded_total)
