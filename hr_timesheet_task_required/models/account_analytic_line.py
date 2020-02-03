# Copyright 2018 ACSONE SA/NV
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_task_required = fields.Boolean(
        string="Is Task Required", related="project_id.is_timesheet_task_required"
    )

    @api.constrains("project_id", "task_id")
    def _check_timesheet_task(self):
        for line in self:
            if line.is_task_required and not line.task_id:
                raise ValidationError(_("You must specify a task for timesheet lines."))
