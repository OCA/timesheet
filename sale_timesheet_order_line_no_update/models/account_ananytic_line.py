import traceback

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.depends(
        "task_id.sale_line_id",
        "project_id.sale_line_id",
        "employee_id",
        "project_id.allow_billable",
    )
    def _compute_so_line(self):
        methods_in_stack = [r.name for r in traceback.extract_stack()]
        if "onchange" in methods_in_stack or "write" in methods_in_stack:
            return
        return super()._compute_so_line()
