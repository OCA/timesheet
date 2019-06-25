# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _analytic_compute_delivered_quantity(self):
        """Set context to read a.a.l unit_amount from unit_amount_rounded"""
        self = self.with_context(timesheet_rounding=True)
        return super()._analytic_compute_delivered_quantity()
