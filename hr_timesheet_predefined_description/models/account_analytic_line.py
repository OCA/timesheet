# Copyright 2024 Tecnativa - Juan José Seguí
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    predefined_description_id = fields.Many2one(
        comodel_name="timesheet.predefined.description", string="Predefined Description"
    )

    @api.model
    def _adjust_name_from_predefined_description(self, vals):
        """Set description on the analytic line if no valid description is provided in
        the dictionary vals and there's a predefined description.
        """
        if "predefined_description_id" in vals and (vals.get("name") or "/") == "/":
            description = self.env["timesheet.predefined.description"].browse(
                vals["predefined_description_id"]
            )
            vals["name"] = description.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._adjust_name_from_predefined_description(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._adjust_name_from_predefined_description(vals)
        return super().write(vals)

    @api.onchange("predefined_description_id")
    def _onchange_predefined_description(self):
        if self.predefined_description_id:
            self.name = self.predefined_description_id.name
