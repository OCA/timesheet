# Copyright 2023 ooops404 - Ilyas
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    new_sale_line_id = fields.Many2one(
        "sale.order.line",
        "Default Sale Order Item",
        copy=False,
    )
    hide_original_sol = fields.Boolean()
    new_sale_line_id_domain = fields.Binary(related="project_id.sale_line_id_domain")

    def default_get(self, fields):
        vals = super(ProjectTask, self).default_get(fields)
        if vals.get("project_id"):
            project = self.env["project.project"].browse(vals["project_id"])
            vals["new_sale_line_id"] = project.sale_line_id.id
        return vals


class ProjectProject(models.Model):
    _inherit = "project.project"

    select_all_project_sale_items = fields.Boolean()
    sale_line_id_domain = fields.Binary(
        compute="_compute_sale_line_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends("select_all_project_sale_items")
    def _compute_sale_line_id_domain(self):
        for rec in self:
            if not rec.select_all_project_sale_items:
                field, value = "order_partner_id", rec.partner_id.id
            else:
                field, value = "order_id", rec.sale_order_id.id
            rec.sale_line_id_domain = [
                ("is_service", "=", True),
                ("is_expense", "=", False),
                (field, "=", value),
                ("state", "in", ["sale", "done"]),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", rec.company_id.id),
            ]

    def update_tasks_default_sol(self):
        for rec in self:
            rec.task_ids.new_sale_line_id = rec.sale_line_id

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.filtered(lambda x: x.sale_line_id).update_tasks_default_sol()
        return res

    def write(self, values):
        res = super().write(values)
        if values.get("sale_line_id"):
            self.update_tasks_default_sol()
        return res
