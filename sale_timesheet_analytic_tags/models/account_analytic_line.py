# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    def _update_analytic_tags_from_task(self, vals):
        task_id = vals.get("task_id")
        if task_id:
            task = self.env["project.task"].browse([task_id])
            tag_ids = task.analytic_tag_ids.ids
            vals["tag_ids"] = [(6, 0, tag_ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_analytic_tags_from_task(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._update_analytic_tags_from_task(vals)
        return super().write(vals)
