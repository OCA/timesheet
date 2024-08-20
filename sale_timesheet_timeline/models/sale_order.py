# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    any_service_line = fields.Boolean(compute="_compute_any_service_line")

    def _compute_any_service_line(self):
        for record in self:
            record.any_service_line = any(
                [x.product_type == "service" for x in record.order_line]
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    task_date_start = fields.Datetime("Task Start")
    task_date_end = fields.Datetime("Task End")
    task_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Task Assignees",
        copy=True,
        context={"active_test": False},
        domain="[('share', '=', False), ('active', '=', True)]",
    )

    def _timesheet_create_task_prepare_values(self, project):
        # Transfer dates and assignees from sales order line
        res = super()._timesheet_create_task_prepare_values(project)
        if self.task_date_start:
            res["planned_date_start"] = self.task_date_start
        if self.task_date_end:
            res["planned_date_end"] = self.task_date_end
            res["date_deadline"] = self.task_date_end
        if self.task_user_ids:
            res["user_ids"] = [Command.link(x.id) for x in self.task_user_ids]
        return res
