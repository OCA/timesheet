# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.onchange("project_id")
    def onchange_project_id(self):
        # Check if 'closed' field exists (provided by project_stage_closed)
        project_stage_closed = (
            "project.task.type" in self.env
            and "closed" in self.env["project.task.type"]._fields
        )

        task = self.task_id
        res = super().onchange_project_id()
        if res is None:
            res = {}
        if self.project_id:  # Show only opened tasks
            task_domain = [("project_id", "=", self.project_id.id)]
            if project_stage_closed:
                task_domain = task_domain + [("stage_id.closed", "=", False)]
            res_domain = res.setdefault("domain", {})
            res_domain.update({"task_id": task_domain})
        else:  # Reset domain for allowing selection of any task
            res["domain"] = {"task_id": []}
        if task.project_id == self.project_id:
            # Restore previous task if belongs to the same project
            self.task_id = task
        return res

    @api.onchange("task_id")
    def _onchange_task_id(self):
        super()._onchange_task_id()

        if self.task_id:
            self.project_id = self.task_id.project_id
