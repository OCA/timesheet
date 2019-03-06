# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    timesheet_negative_unit_amount = fields.Boolean(
        related='company_id.timesheet_negative_unit_amount',
        string="Negative Quantities",
        help="Allow negative hours.")
