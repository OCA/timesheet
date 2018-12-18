# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    sheet_range = fields.Selection(
        related='company_id.sheet_range',
        string="Timesheet Sheet Range",
        help="The range of your Timesheet Sheet.",
        readonly=False)

    timesheet_week_start = fields.Selection(
        related='company_id.timesheet_week_start',
        string="Week Start Day",
        help="Starting day for Timesheet Sheets.",
        readonly=False)
