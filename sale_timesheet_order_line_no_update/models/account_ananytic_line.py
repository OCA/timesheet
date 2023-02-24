from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def _timesheet_determine_sale_line(self, task, employee, project):
        if task and task.allow_billable and task.sale_line_id:
            if task.pricing_type == "fixed_rate":
                if task.new_sale_line_id:
                    return task.new_sale_line_id
        return super(AccountAnalyticLine, self)._timesheet_determine_sale_line(
            task, employee, project
        )

    @api.onchange("employee_id")
    def _onchange_task_id_employee_id(self):
        if self.project_id and self.task_id.allow_billable:  # timesheet only
            if (
                self.task_id.bill_type == "customer_task"
                or self.task_id.pricing_type == "fixed_rate"
            ):
                if self.task_id.new_sale_line_id:
                    self.so_line = self.task_id.new_sale_line_id
                else:
                    super(AccountAnalyticLine, self)._onchange_task_id_employee_id()