from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    timesheet_product_id = fields.Many2one(
        "product.product",
        string="Purchase Timesheet Product",
    )
