# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    timesheet_sheets_autodraft = fields.Boolean(
        related="company_id.timesheet_sheets_autodraft",
        string="Timesheet Sheets Auto-draft",
        help=(
            "Auto-draft Timesheet Sheets whenever a Timesheet entry is created"
            " or modified to ensure it's covered by a relevant Timesheet"
            " Sheet"
        ),
        readonly=False,
    )
