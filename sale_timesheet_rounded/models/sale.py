# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        # If we land here is only because we are dealing w/ SO lines
        # having `qty_delivered_method` equal to `analytic` or `timesheet`.
        # The 1st case matches expenses lines the latter TS lines.
        # Expenses are already discarded in our a.a.l. overrides
        # so it's fine to set the ctx key here anyway.
        self = self.with_context(timesheet_rounding=True)
        return super()._get_delivered_quantity_by_analytic(additional_domain)

    @api.depends("analytic_line_ids.unit_amount_rounded")
    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
