# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    service_tracking = fields.Selection(
        selection_add=[
            ("task_in_project", "Create a task in sale order's project")
        ],
    )

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        """Reset project when using this setting."""
        res = super()._onchange_service_tracking()
        if self.service_tracking == 'task_in_project':
            self.project_id = False
        return res
