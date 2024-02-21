# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    account_id = fields.Many2one(
        compute="_compute_account_id",
        store=True,
        readonly=False,
    )

    @api.depends("task_id.analytic_account_id")
    def _compute_account_id(self):
        """Change the analytic account non billed lines."""
        timesheet_ids = self.filtered(
            lambda t: not t.is_so_line_edited
            and t._is_not_billed()
            and t.task_id.analytic_account_id
        )
        for timesheet in timesheet_ids:
            timesheet.account_id = timesheet.task_id.analytic_account_id
