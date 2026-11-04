# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    timesheet_portal_visibility = fields.Selection(
        [
            ("invoiced", "Invoiced only"),
            ("all", "All timesheets"),
        ],
        default="all",
    )
