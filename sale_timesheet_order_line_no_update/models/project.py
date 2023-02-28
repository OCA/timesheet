import json

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    new_sale_line_id = fields.Many2one(
        "sale.order.line",
        "Default Sale Order Item",
        copy=False,
    )
    hide_original_sol = fields.Boolean()

    new_sale_line_id_domain = fields.Char(
        compute="_compute_new_sale_line_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends("project_id", "project_id.select_all_project_sale_items")
    def _compute_new_sale_line_id_domain(self):
        for rec in self:
            if not self.project_id.select_all_project_sale_items:
                rec.new_sale_line_id_domain = json.dumps(
                    [
                        ("is_service", "=", True),
                        ("is_expense", "=", False),
                        ("order_id", "=", rec.sale_order_id.id),
                        ("state", "in", ["sale", "done"]),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )
            else:
                rec.new_sale_line_id_domain = json.dumps(
                    [
                        ("is_service", "=", True),
                        ("is_expense", "=", False),
                        ("order_partner_id", "=", rec.partner_id.id),
                        ("state", "in", ["sale", "done"]),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )


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
            if not self.select_all_project_sale_items:
                rec.sale_line_id_domain = json.dumps(
                    [
                        ("is_service", "=", True),
                        ("is_expense", "=", False),
                        ("order_id", "=", rec.sale_order_id.id),
                        ("state", "in", ["sale", "done"]),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )
            else:
                rec.sale_line_id_domain = json.dumps(
                    [
                        ("is_service", "=", True),
                        ("is_expense", "=", False),
                        ("order_partner_id", "=", rec.partner_id.id),
                        ("state", "in", ["sale", "done"]),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )

    @api.onchange("sale_line_id")
    def _onchange_sale_line_id(self):
        task_ids = self.env["project.task"].search([("project_id", "in", self.ids)])
        task_ids.write({"new_sale_line_id": self.sale_line_id})
