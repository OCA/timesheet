# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = "project.task"

    billable_type = fields.Selection(
        selection_add=[
            ("employee_role_rate", "At Employee/Role Rate"),
        ],
    )

    @api.multi
    def _compute_sale_order_id(self):
        super()._compute_sale_order_id()
        for task in self:
            if task.billable_type == "employee_role_rate":
                task.sale_order_id = task.project_id.sale_order_id

    @api.multi
    def _compute_billable_type(self):
        super()._compute_billable_type()
        for task in self:
            if task.project_id.billable_type == "employee_role_rate":
                task.billable_type = task.project_id.billable_type
