from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        ondelete="set null",
        compute="_compute_analytic_account_id",
        store=True,
        readonly=False,
        domain="[('company_id', '=?', company_id)]",
        help="Analytic account to which this task and its timesheets are linked.",
    )

    @api.depends("project_id.account_id")
    def _compute_analytic_account_id(self):
        for task in self:
            task.analytic_account_id = task.project_id.account_id
