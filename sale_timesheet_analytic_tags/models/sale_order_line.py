# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        res = super()._timesheet_create_task_prepare_values(project)
        tag_ids = self.analytic_tag_ids.ids
        res["analytic_tag_ids"] = [(6, 0, tag_ids)]
        return res
