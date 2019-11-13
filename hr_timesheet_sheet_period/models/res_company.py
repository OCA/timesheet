# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

SHEET_RANGE_PAYROLL_PERIOD = 100


class ResCompany(models.Model):
    _inherit = 'res.company'

    sheet_range = fields.Selection(
        selection_add=[
            (SHEET_RANGE_PAYROLL_PERIOD, 'Payroll Period'),
        ],
    )
