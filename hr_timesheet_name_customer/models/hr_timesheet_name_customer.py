# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class NameCustomer(models.Model):
    _inherit = "account.analytic.line"

    name_customer = fields.Char(
        string="Customer Description",
        compute="_compute_name_customer",
        store=True,
        readonly=False,
    )

    @api.depends("name")
    def _compute_name_customer(self):
        for rec in self:
            if not rec.name_customer and rec.name:
                rec.name_customer = rec.name
