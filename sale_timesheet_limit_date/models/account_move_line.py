# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, values):
        # unlink lines from invoice if they under limit_date
        res = super().create(values)
        to_clean = self.env["account.analytic.line"]
        for move_line in res:
            if (
                move_line.move_id.move_type == "out_invoice"
                and move_line.move_id.state == "draft"
                and move_line.move_id.timesheet_limit_date
            ):
                sale_line_delivery = move_line.sale_line_ids.filtered(
                    lambda sol: sol.product_id.service_policy == "delivered_timesheet"
                    and sol.product_id.service_type == "timesheet"
                )
                if sale_line_delivery:
                    to_clean += self.env["account.analytic.line"].search(
                        [
                            ("timesheet_invoice_id", "=", move_line.move_id.id),
                            ("date", ">", move_line.move_id.timesheet_limit_date),
                        ]
                    )
        to_clean.write({"timesheet_invoice_id": False})
        return res
