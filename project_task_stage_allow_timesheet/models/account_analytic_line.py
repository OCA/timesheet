# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    task_id = fields.Many2one(
        domain=lambda self: self._get_task_domain(),
    )

    @api.constrains('task_id')
    def _check_task_allow_timesheet(self):
        for rec in self:
            task = rec.task_id
            stage = task.stage_id
            if task and not stage.allow_timesheet:
                raise ValidationError(_(
                    "You can't link a timesheet line to a task if its stage "
                    "doesn't allow it. (Task: %s, Stage: %s)"
                ) % (
                    task.display_name,
                    stage.display_name,
                ))

    @api.model
    def _get_task_domain(self):
        return "[" \
               "('project_id', '=', project_id)," \
               "('stage_id.allow_timesheet', '=', True)," \
               "]"
