# Copyright 2025 Miquel Pascual López(APSL-Nagarro)<mpascual@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    non_billable = fields.Boolean(
        related="time_type_id.non_billable", string="Non Billable", readonly=True
    )

    @api.onchange("time_type_id")
    def _onchange_time_type_id_non_billable(self):
        for line in self:
            if line.time_type_id and line.time_type_id.non_billable:
                line.exclude_from_sale_order = True
            else:
                line.exclude_from_sale_order = False
