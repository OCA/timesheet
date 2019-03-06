# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    timesheet_negative_unit_amount = fields.Boolean(
        string="Negative Quantities",
        default=False,
        help="Allow negative hours.")
