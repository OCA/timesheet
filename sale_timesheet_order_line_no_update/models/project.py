from odoo import fields, models


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

    def default_get(self, fields):
        vals = super(ProjectTask, self).default_get(fields)
        # vals['hide_original_sol'] = self.env['ir.default'].get(
        #     'project.task', 'hide_original_sol'
        # )
        return vals
