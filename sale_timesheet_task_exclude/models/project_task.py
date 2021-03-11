# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    exclude_from_sale_order = fields.Boolean(
        string="Exclude from Sale Order",
        help=(
            "Checking this would exclude any timesheet entries logged towards"
            " this task from Sale Order"
        ),
    )

    @api.depends(
        "sale_line_id",
        "project_id",
        "allow_billable",
        "non_allow_billable",
        "exclude_from_sale_order",
    )
    def _compute_sale_order_id(self):
        super(ProjectTask, self)._compute_sale_order_id()
        excluded = self.filtered("exclude_from_sale_order")
        for task in excluded:
            task.sale_order_id = False

    def write(self, vals):
        res = super().write(vals)
        if "exclude_from_sale_order" in vals:
            # If tasks changed their exclude_from_sale_order, update all AALs
            # that have not been invoiced yet
            for timesheet in self.timesheet_ids.filtered(
                lambda line: not line.timesheet_invoice_id
            ):
                timesheet._onchange_task_id_employee_id()
        return res
