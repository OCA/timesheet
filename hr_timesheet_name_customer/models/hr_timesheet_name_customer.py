# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class NameCustomer(models.Model):
    _inherit = "account.analytic.line"

    name_customer = fields.Char(string="Customer Description")
    """override create method, initialize name_customer"""

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name_customer"):
                vals["name_customer"] = vals["name"]
        return super(NameCustomer, self).create(vals_list)
