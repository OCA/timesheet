# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    timesheet_product_id = fields.Many2one(
        "product.product",
        related="company_id.timesheet_product_id",
        string="Purchase Timesheet Product",
        readonly=False,
    )
