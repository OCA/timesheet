from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    milestone_id = fields.Many2one(
        string="Milestone",
        comodel_name="project.milestone",
        ondelete="set null",
        related="task_id.milestone_id",
        store=1,
    )
