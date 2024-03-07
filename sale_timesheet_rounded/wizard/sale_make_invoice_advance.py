# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        """Override method from sale/wizard/sale_make_invoice_advance.py

        When the user want to invoice the timesheets to the SO
        up to a specific period then we need to recompute the
        qty_to_invoice for each product_id in sale.order.line,
        before creating the invoice.
        """
        return super(
            SaleAdvancePaymentInv, self.with_context(timesheet_no_recompute=True)
        ).create_invoices()
