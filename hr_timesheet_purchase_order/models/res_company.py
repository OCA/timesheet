# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    timesheet_product_id = fields.Many2one(
        "product.product",
        string="Purchase Timesheet Product",
    )
