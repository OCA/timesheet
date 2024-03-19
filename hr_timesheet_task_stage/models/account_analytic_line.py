# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_task_closed = fields.Boolean(related="task_id.stage_id.fold")

    def action_open_task(self):
        for line in self.filtered("task_id.project_id"):
            stage = self.env["project.task.type"].search(
                [
                    ("project_ids", "=", line.task_id.project_id.id),
                    ("fold", "=", False),
                ],
                limit=1,
            )
            if not stage:  # pragma: no cover
                raise UserError(
                    _(
                        'There isn\'t any stage with "Closed" unchecked.'
                        " Please unmark any."
                    )
                )
            line.task_id.write({"stage_id": stage.id})

    def action_close_task(self):
        for line in self.filtered("task_id.project_id"):
            stage = self.env["project.task.type"].search(
                [("project_ids", "=", line.task_id.project_id.id), ("fold", "=", True)],
                limit=1,
            )
            if not stage:  # pragma: no cover
                raise UserError(
                    _(
                        'There isn\'t any stage with "Closed" checked. Please'
                        " mark any."
                    )
                )
            line.task_id.write({"stage_id": stage.id})

    def action_toggle_task_stage(self):
        for line in self.filtered("task_id.project_id"):
            if line.is_task_closed:
                line.action_open_task()
            else:
                line.action_close_task()
