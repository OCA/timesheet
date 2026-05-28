# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    timesheet_edit_level = fields.Selection(
        related="company_id.timesheet_edit_level",
        readonly=False,
        string="Timesheet Edit Level for Time Off",
        help="""
            Indicates who can edit generated timesheets
        """,
    )
