# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        """This mimicks upstream core that duplicates this code."""
        res = super()._onchange_service_tracking()
        if self.service_tracking == 'task_in_project':
            self.project_id = False
        return res
