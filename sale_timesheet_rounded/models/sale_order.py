# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    timesheet_total_duration_rounded = fields.Integer(
        string="Rounded Timesheet Total Duration",
        compute="_compute_timesheet_total_duration_rounded",
        compute_sudo=True,
        groups="hr_timesheet.group_hr_timesheet_user",
    )

    def _compute_timesheet_total_duration_rounded(self):
        group_data = self.env["account.analytic.line"]._read_group(
            [("order_id", "in", self.ids), ("project_id", "!=", False)],
            ["order_id"],
            ["unit_amount_rounded:sum"],
        )
        rounded_dict = {order.id: rounded for order, rounded in group_data}
        for sale_order in self:
            total_time = sale_order.company_id.project_time_mode_id._compute_quantity(
                rounded_dict.get(sale_order.id, 0.0),
                sale_order.timesheet_encode_uom_id,
                rounding_method="HALF-UP",
            )
            sale_order.timesheet_total_duration_rounded = round(total_time)
