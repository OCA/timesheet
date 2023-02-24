from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    new_sale_line_id = fields.Many2one("sale.order.line")
