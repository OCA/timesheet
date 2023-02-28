from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    new_sale_line_id = fields.Many2one(
        "sale.order.line",
        "Default Sale Order Item",
        copy=False,
        domain="[('is_service', '=', True), ('is_expense', '=', False), "
        "('order_id', '=', sale_order_id), "
        "('state', 'in', ['sale', 'done']), '|', ('company_id', '=', False), "
        "('company_id', '=', company_id)]",
    )
    hide_original_sol = fields.Boolean()

    def write(self, values):
        res = super(ProjectTask, self).write(values)
        return res


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.onchange("sale_line_id")
    def _onchange_sale_line_id(self):
        task_ids = self.env["project.task"].search([("project_id", "in", self.ids)])
        task_ids.write({"new_sale_line_id": self.sale_line_id})
