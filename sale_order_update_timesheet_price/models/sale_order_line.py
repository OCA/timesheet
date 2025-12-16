from odoo import api, fields, models
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_update_price_button = fields.Boolean(
        compute="_compute_show_update_price_button"
    )
    price_unit_updated = fields.Boolean(
        help="Technical field to know if the price has been updated"
    )

    @api.depends("qty_invoiced", "qty_delivered_method", "name")
    def _compute_show_update_price_button(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        for rec in self:
            rec.show_update_price_button = (
                not float_is_zero(rec.qty_invoiced, precision_digits=precision)
                and rec.qty_delivered_method == "timesheet"
                and not rec.price_unit_updated
            )
