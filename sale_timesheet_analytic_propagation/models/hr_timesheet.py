from odoo import api, fields, models


class HrTimehseet(models.Model):
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
            lambda t: t.task_id.analytic_account_id
            and not t.is_so_line_edited
            and t._is_not_billed()
        )
        for timesheet in timesheet_ids:
            timesheet.account_id = timesheet.task_id.analytic_account_id
