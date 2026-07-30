# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    timesheet_suspense_account_id = fields.Many2one(
        comodel_name="account.account",
    )
    timesheet_cost_account_id = fields.Many2one(
        comodel_name="account.account",
    )
    timesheet_cost_journal_id = fields.Many2one(
        comodel_name="account.journal",
    )
