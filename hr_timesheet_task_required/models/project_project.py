# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    is_timesheet_task_required = fields.Boolean(
        string="Require Tasks on Timesheets",
        default=lambda self: self._default_is_timesheet_task_required(),
    )

    @api.model
    def _default_is_timesheet_task_required(self):
        company = self.env["res.company"].browse(
            self._context.get("company_id", self.env.user.company_id.id)
        )
        return company.is_timesheet_task_required
