# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    task_id = fields.Many2one(
        domain=lambda self: self._get_task_domain(),
    )

    @api.constrains("task_id")
    def _check_task_allow_timesheet(self):
        for rec in self:
            task = rec.task_id
            stage = task.stage_id
            if task and stage and not stage.allow_timesheet:
                raise ValidationError(
                    _(
                        "You can't link a timesheet line to a task if its stage"
                        " doesn't allow it. (Task: %(task_name)s, Stage: %(stage_name)s)"
                    )
                    % {
                        "task_name": task.display_name,
                        "stage_name": stage.display_name,
                    }
                )

    @api.model
    def _get_task_domain(self):
        return (
            "["
            "('project_id', '=', project_id),"
            "('stage_id.allow_timesheet', '=', True),"
            "]"
        )
