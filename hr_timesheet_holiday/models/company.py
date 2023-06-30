# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    """Add hours per day to company"""

    _inherit = "res.company"

    timesheet_hours_per_day = fields.Float(digits=(2, 2), default=8.0)
