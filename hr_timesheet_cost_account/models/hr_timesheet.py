# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    timesheet_costing_id = fields.Many2one(
        comodel_name="hr.timesheet.costing",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
