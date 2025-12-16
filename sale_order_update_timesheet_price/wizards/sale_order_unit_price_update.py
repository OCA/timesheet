# Copyright 2017-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrderUnitPriceUpdate(models.TransientModel):
    _name = "sale.order.unit.price.update"
    _description = "Update unit price on sale order line partially invoiced"

    order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order Line",
        required=True,
        default=lambda self: self._default_order_line_id(),
    )
    order_line_name = fields.Text(related="order_line_id.name", readonly=True)
    old_unit_price = fields.Float(related="order_line_id.price_unit", readonly=True)
    new_unit_price = fields.Float(required=True, digits="Product Price")
    old_line_prefix = fields.Char(default="[Old Rate]")

    def _default_order_line_id(self):
        sol_id = self.env.context.get("active_id")
        return self.env["sale.order.line"].browse(sol_id)

    def _prepare_default_line_values(self):
        return {
            "order_id": self.order_line_id.order_id.id,
            "project_id": self.order_line_id.project_id.id,
            "task_id": self.order_line_id.task_id.id,
            "price_unit": self.new_unit_price,
            "product_uom_qty": max(
                self.order_line_id.product_uom_qty - self.order_line_id.qty_invoiced, 1
            ),
        }

    def action_update_unit_price(self):
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get("Product Price")
        if (
            float_compare(
                self.new_unit_price, self.old_unit_price, precision_digits=precision
            )
            == 0
        ):
            raise UserError(
                self.env._("The new unit price is the same as the old one.")
            )

        # create a new SO line with same product, description, remaining quantity,
        # taxes, etc... and the new unit price
        default_vals = self._prepare_default_line_values()
        new_line = self.order_line_id.copy(default=default_vals)

        # relink all projects, tasks, milestones linked to the old line to the new line
        self.env["project.project"].sudo().search(
            [
                ("sale_line_id", "=", self.order_line_id.id),
            ]
        ).write({"sale_line_id": new_line.id})
        self.env["project.task"].sudo().search(
            [
                ("sale_line_id", "=", self.order_line_id.id),
            ]
        ).write({"sale_line_id": new_line.id})
        self.env["project.milestone"].sudo().search(
            [
                ("project_id", "=", new_line.project_id.id),
                ("sale_line_id", "=", self.order_line_id.id),
            ]
        ).write({"sale_line_id": new_line.id})
        self.env["project.sale.line.employee.map"].sudo().search(
            [
                ("project_id", "=", new_line.project_id.id),
                ("sale_line_id", "=", self.order_line_id.id),
            ]
        ).write({"sale_line_id": new_line.id})

        # prefix the description of the old line and set it updated
        self.order_line_id.name = (
            self.old_line_prefix.strip() + " " + self.order_line_name
        )
        self.order_line_id.price_unit_updated = True
