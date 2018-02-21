# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    @api.constrains(
        'project_id',
        'task_id',
    )
    def _check_timesheet_task(self):
        for rec in self:
            if rec.project_id and not rec.task_id:
                raise ValidationError(_(
                    "You must specify a task for timesheet lines."))
