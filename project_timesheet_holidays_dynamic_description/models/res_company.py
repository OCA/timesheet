# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    dynamic_timesheet_description = fields.Boolean(
        string="Dynamic Description",
        default=True,
        help="If enabled, timesheets generated from time off "
        "will contains the leave description.",
    )
