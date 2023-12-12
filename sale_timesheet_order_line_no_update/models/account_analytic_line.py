# Copyright 2023 ooops404 - Ilyas
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.depends(
        "task_id.sale_line_id",
        "project_id.sale_line_id",
        "project_id.allow_billable",
        "employee_id",
    )
    def _compute_so_line(self):
        skip_ids = self.filtered(lambda t: t.task_id and t.task_id.new_sale_line_id)
        self -= skip_ids
        if self:
            super(
                AccountAnalyticLine, self.filtered(lambda t: not t.is_so_line_edited)
            )._compute_so_line()

    @api.model
    def _timesheet_determine_sale_line(self, task, employee, project):
        if (
            task
            and task.allow_billable
            and task.sale_line_id
            and task.pricing_type == "fixed_rate"
            and task.new_sale_line_id
        ):
            return task.new_sale_line_id
        return super()._timesheet_determine_sale_line(task, employee, project)

    @api.onchange("employee_id")
    def _onchange_task_id_employee_id(self):
        if self.project_id and self.task_id.allow_billable:  # timesheet only
            if self.task_id.new_sale_line_id and (
                self.task_id.bill_type == "customer_task"
                or self.task_id.pricing_type == "fixed_rate"
            ):
                self.so_line = self.task_id.new_sale_line_id
            else:
                super(AccountAnalyticLine, self)._onchange_task_id_employee_id()
