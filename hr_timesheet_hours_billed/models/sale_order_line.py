# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.osv import expression


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "qty_delivered_method",
        "analytic_line_ids.so_line",
        "analytic_line_ids.unit_amount_billed",
        "analytic_line_ids.product_uom_id",
        "analytic_line_ids.approved",
    )
    def _compute_qty_delivered(self):
        """This method compute the delivered quantity of the SO lines:
        it covers the case provide by sale module, aka
        expense/vendor bills (sum of unit_amount_billed of AAL), and manual case.
        """

        return super(SaleOrderLine, self)._compute_qty_delivered()

    def _get_delivered_quantity_by_analytic(self, additional_domain):
        """Retrieve delivered quantity by line
        :param additional_domain: domain to restrict AAL to include in computation
        (required since timesheet is an AAL with a project ...)
        """
        result = {}

        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group analytic lines by product uom and so line
        domain = expression.AND(
            [
                [
                    ("so_line", "in", self.ids),
                ],
                additional_domain,
            ]
        )
        data = self.env["account.analytic.line"].read_group(
            domain,
            ["so_line", "unit_amount_billed", "approved", "product_uom_id"],
            ["product_uom_id", "so_line", "approved"],
            lazy=False,
        )

        # convert uom and sum all unit_amount_billed of analytic lines
        # to get the delivered qty of SO lines
        # browse so lines and product uoms here to make them share the same prefetch
        lines = self.browse([item["so_line"][0] for item in data])
        lines_map = {line.id: line for line in lines}
        product_uom_ids = [
            item["product_uom_id"][0] for item in data if item["product_uom_id"]
        ]
        product_uom_map = {
            uom.id: uom for uom in self.env["uom.uom"].browse(product_uom_ids)
        }
        for item in data:
            if not item["product_uom_id"]:
                continue
            so_line_id = item["so_line"][0]
            so_line = lines_map[so_line_id]
            result.setdefault(so_line_id, 0.0)
            uom = product_uom_map.get(item["product_uom_id"][0])
            if item.get("approved"):
                if so_line.product_uom.category_id == uom.category_id:
                    qty = uom._compute_quantity(
                        item["unit_amount_billed"],
                        so_line.product_uom,
                        rounding_method="HALF-UP",
                    )
                else:
                    qty = item["unit_amount_billed"]
                result[so_line_id] += qty

        return result
