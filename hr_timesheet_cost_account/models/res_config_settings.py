# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    timesheet_suspense_account_id = fields.Many2one(
        related="company_id.timesheet_suspense_account_id",
        readonly=False,
    )
    timesheet_cost_account_id = fields.Many2one(
        related="company_id.timesheet_cost_account_id",
        readonly=False,
    )
    timesheet_cost_journal_id = fields.Many2one(
        related="company_id.timesheet_cost_journal_id",
        readonly=False,
    )
