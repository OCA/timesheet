# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import odoo
from odoo import fields

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@odoo.tests.tagged("post_install", "-at_install")
class TestRounded(TestCommonSaleTimesheet):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "partner_invoice_id": cls.partner_a.id,
                "partner_shipping_id": cls.partner_a.id,
            }
        )
        cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order.id,
                "name": cls.product_delivery_timesheet2.name,
                "product_id": cls.product_delivery_timesheet2.id,
                "product_uom_qty": 1,
                "product_uom": cls.product_delivery_timesheet2.uom_id.id,
                "price_unit": cls.product_delivery_timesheet2.list_price,
            }
        )
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
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Plan sale timesheet",
            }
        )
        cls.avg_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "AVG account",
                "plan_id": cls.analytic_plan.id,
            }
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
        # Temporarily disable rounding for this test
        self.project_global.write({"timesheet_rounding_method": "NO"})
        # Create at least one line to ensure the loop executes
        self.create_analytic_line(unit_amount=1)
        lines = self.env["account.analytic.line"].search([])
        for line in lines:
            self.assertEqual(line.unit_amount_rounded, line.unit_amount)
        # Restore rounding for other tests
        self.project_global.write({"timesheet_rounding_method": "UP"})

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
        groupby = ["product_uom_id", "so_line"]
        aggregates = ["unit_amount:sum"]

        data_ctx_f = line._read_group(
            domain,
            groupby,
            aggregates,
        )
        self.assertEqual(
            data_ctx_f[0][len(groupby) + aggregates.index("unit_amount:sum")], 1.0
        )

        data_ctx_t = line.with_context(timesheet_rounding=True)._read_group(
            domain,
            groupby,
            aggregates,
        )
        self.assertEqual(
            data_ctx_t[0][len(groupby) + aggregates.index("unit_amount:sum")], 2.0
        )

        self.create_analytic_line(unit_amount=1.1)
        data_ctx_f = line.with_context(timesheet_rounding=False)._read_group(
            domain,
            groupby,
            aggregates,
        )
        self.assertEqual(
            data_ctx_f[0][len(groupby) + aggregates.index("unit_amount:sum")], 2.1
        )

        data_ctx_f = line.with_context(timesheet_rounding=True)._read_group(
            domain,
            groupby,
            aggregates,
        )
        self.assertEqual(
            data_ctx_f[0][len(groupby) + aggregates.index("unit_amount:sum")], 4.25
        )

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
        rounding_method = "HALF-UP"
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
        inv_line = account_move.line_ids.filtered(
            lambda line: line.product_id == prd_ts_id
        )
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
        account_move.action_post()
        prd_ts_id = self.product_delivery_timesheet2
        account_move.button_draft()
        # the unit_amount_rounded is not changed
        self.assertEqual(analytic_line.unit_amount_rounded, unit_amount_rounded)
        # the invoiced qty remains the same
        inv_line = account_move.line_ids.filtered(
            lambda line: line.product_id == prd_ts_id
        )
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
        inv_line = account_move.line_ids.filtered(
            lambda line: line.product_id == prd_ts_id
        )
        self.assertEqual(inv_line.quantity, unit_amount_rounded_total)

    def test_read_with_specific_fields_without_rounded(self):
        """Test read with specific fields when unit_amount_rounded is not in the list.

        When reading with timesheet_rounding context and specific fields,
        the unit_amount value should be replaced by unit_amount_rounded.
        """
        line = self.create_analytic_line(unit_amount=1)
        # Test with specific fields and timesheet_rounding context
        fields_to_read = ["unit_amount", "name", "date"]
        result = line.with_context(timesheet_rounding=True).read(fields_to_read)
        # unit_amount should be replaced by unit_amount_rounded (2.0)
        self.assertEqual(result[0]["unit_amount"], 2.0)
        # Verify that unit_amount_rounded is in the result even if not requested
        self.assertIn("unit_amount_rounded", result[0])

    def test_read_with_specific_fields_with_rounded(self):
        """Test read with specific fields including unit_amount_rounded.

        The unit_amount value should still be replaced by unit_amount_rounded.
        """
        line = self.create_analytic_line(unit_amount=1)
        # Test with unit_amount_rounded already in fields list
        fields_to_read = ["unit_amount", "unit_amount_rounded", "name"]
        result = line.with_context(timesheet_rounding=True).read(fields_to_read)
        # unit_amount should be replaced by unit_amount_rounded (2.0)
        self.assertEqual(result[0]["unit_amount"], 2.0)
        self.assertEqual(result[0]["unit_amount_rounded"], 2.0)

    def test_read_without_fields_list(self):
        """Test read without specifying fields.

        When no fields are specified, all fields should be read and
        unit_amount should be replaced by unit_amount_rounded when context is set.
        """
        line = self.create_analytic_line(unit_amount=1)
        # Test without specifying fields
        result = line.with_context(timesheet_rounding=True).read()
        # unit_amount should be replaced by unit_amount_rounded (2.0)
        self.assertEqual(result[0]["unit_amount"], 2.0)
        self.assertEqual(result[0]["unit_amount_rounded"], 2.0)

    def test_read_without_unit_amount_field(self):
        """Test read with fields that don't include unit_amount.

        The rounding logic should be skipped when unit_amount is not requested.
        """
        line = self.create_analytic_line(unit_amount=1)
        # Test with fields that don't include unit_amount
        fields_to_read = ["name", "date", "project_id"]
        result = line.with_context(timesheet_rounding=True).read(fields_to_read)
        # unit_amount should not be in result
        self.assertNotIn("unit_amount", result[0])

    def test_read_group_with_zero_rounded_amount(self):
        """Test _read_group when unit_amount_rounded is 0.

        When unit_amount_rounded is 0 or False, the original unit_amount
        should not be replaced in the aggregation result.
        """
        line = self.env["account.analytic.line"]
        # Create line with unit_amount_rounded = 0
        analytic_line = self.create_analytic_line(unit_amount=1)
        analytic_line.unit_amount_rounded = 0

        domain = [("project_id", "=", self.project_global.id)]
        groupby = ["product_uom_id"]
        aggregates = ["unit_amount:sum"]

        data = line.with_context(timesheet_rounding=True)._read_group(
            domain,
            groupby,
            aggregates,
        )
        # When unit_amount_rounded is 0, unit_amount should remain as is
        # The line 115 condition is False, so no replacement happens
        self.assertEqual(
            data[0][len(groupby) + aggregates.index("unit_amount:sum")], 1.0
        )

    def test_read_group_without_timesheet_rounding_context(self):
        """Test _read_group without timesheet_rounding context.

        Without the timesheet_rounding context, unit_amount should remain unchanged.
        """
        line = self.env["account.analytic.line"]
        self.create_analytic_line(unit_amount=1)

        domain = [("project_id", "=", self.project_global.id)]
        groupby = ["product_uom_id"]
        aggregates = ["unit_amount:sum"]

        # Without timesheet_rounding context
        data = line.with_context(timesheet_rounding=False)._read_group(
            domain,
            groupby,
            aggregates,
        )
        # Should return original unit_amount (1.0), not rounded
        self.assertEqual(
            data[0][len(groupby) + aggregates.index("unit_amount:sum")], 1.0
        )

    def test_read_group_with_unit_amount_rounded_already_in_aggregates(self):
        """Test _read_group when unit_amount_rounded:sum is already in aggregates.

        Both aggregates should be present and unit_amount should be replaced.
        """
        line = self.env["account.analytic.line"]
        self.create_analytic_line(unit_amount=1)

        domain = [("project_id", "=", self.project_global.id)]
        groupby = ["product_uom_id"]
        aggregates = ["unit_amount:sum", "unit_amount_rounded:sum"]

        data = line.with_context(timesheet_rounding=True)._read_group(
            domain,
            groupby,
            aggregates,
        )
        # Both aggregates should be present
        self.assertEqual(
            data[0][len(groupby) + aggregates.index("unit_amount:sum")], 2.0
        )
        self.assertEqual(
            data[0][len(groupby) + aggregates.index("unit_amount_rounded:sum")], 2.0
        )

    def test_read_group_without_unit_amount_sum(self):
        """Test _read_group without unit_amount:sum in aggregates.

        When unit_amount:sum is not in aggregates, no replacement should occur.
        """
        line = self.env["account.analytic.line"]
        self.create_analytic_line(unit_amount=1)

        domain = [("project_id", "=", self.project_global.id)]
        groupby = ["product_uom_id"]
        aggregates = ["id:count"]

        data = line.with_context(timesheet_rounding=True)._read_group(
            domain,
            groupby,
            aggregates,
        )
        # Should just return count, no unit_amount manipulation
        self.assertEqual(data[0][len(groupby)], 1)

    def test_read_with_timesheet_rounding_false(self):
        """Test read with timesheet_rounding=False.

        Without timesheet_rounding context, unit_amount should not be modified.
        """
        line = self.create_analytic_line(unit_amount=1)
        result = line.with_context(timesheet_rounding=False).read(["unit_amount"])
        # Should return original unit_amount (1.0), not rounded
        self.assertEqual(result[0]["unit_amount"], 1.0)

    def test_read_with_zero_unit_amount_rounded(self):
        """Test read when unit_amount_rounded is 0.

        When unit_amount_rounded is 0, it should not replace unit_amount.
        """
        line = self.create_analytic_line(unit_amount=1)
        line.unit_amount_rounded = 0
        result = line.with_context(timesheet_rounding=True).read(["unit_amount"])
        # When unit_amount_rounded is 0, unit_amount should not be replaced
        self.assertEqual(result[0]["unit_amount"], 1.0)
        self.assertEqual(result[0]["unit_amount_rounded"], 0.0)

    def test_wizard_create_invoices_with_timesheet_no_recompute(self):
        """Test creating invoices through sale advance payment wizard.

        When invoicing through the wizard, the timesheet_no_recompute context
        should be used to prevent recomputing unit_amount_rounded.
        """
        # Create timesheet lines with custom rounded amount
        analytic_line = self.create_analytic_line(unit_amount=2)
        unit_amount_rounded = 7
        analytic_line.unit_amount_rounded = unit_amount_rounded

        # Verify there's something to invoice
        self.assertGreater(self.sale_order.order_line.qty_to_invoice, 0)

        # Create and execute wizard for invoicing delivered quantities
        wizard_env = self.env["sale.advance.payment.inv"].with_context(
            active_model="sale.order",
            active_ids=self.sale_order.ids,
            active_id=self.sale_order.id,
        )
        wizard = wizard_env.create({"advance_payment_method": "delivered"})

        # This calls the overridden create_invoices method
        wizard.create_invoices()

        # Verify invoice was created
        invoice = self.sale_order.invoice_ids
        self.assertTrue(invoice, "Invoice should have been created")

        # Verify that unit_amount_rounded was not recomputed
        self.assertEqual(
            analytic_line.unit_amount_rounded,
            unit_amount_rounded,
            "unit_amount_rounded should remain unchanged after invoicing",
        )
