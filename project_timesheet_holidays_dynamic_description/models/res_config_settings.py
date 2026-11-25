# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    dynamic_timesheet_description = fields.Boolean(
        related="company_id.dynamic_timesheet_description",
        readonly=False,
    )
