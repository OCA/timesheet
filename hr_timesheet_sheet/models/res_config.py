# Copyright 2018 ForgeFlow, S.L.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    sheet_range = fields.Selection(
        related="company_id.sheet_range",
        string="Timesheet Sheet Range",
        help="The range of your Timesheet Sheet.",
        readonly=False,
    )

    timesheet_week_start = fields.Selection(
        related="company_id.timesheet_week_start",
        string="Week Start Day",
        help="Starting day for Timesheet Sheets.",
        readonly=False,
    )

    timesheet_sheet_review_policy = fields.Selection(
        related="company_id.timesheet_sheet_review_policy", readonly=False
    )
