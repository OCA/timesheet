# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_employee = fields.Boolean(string='Is an Employee')
