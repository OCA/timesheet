# © 2023 ooops404
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

    new_sale_line_id_domain = fields.Char(related="project_id.sale_line_id_domain")


class ProjectProject(models.Model):
    _inherit = "project.project"

    select_all_project_sale_items = fields.Boolean()
    sale_line_id_domain = fields.Char(
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

    @api.onchange("sale_line_id")
    def _onchange_sale_line_id(self):
        self.task_ids.write({"new_sale_line_id": self.sale_line_id})
