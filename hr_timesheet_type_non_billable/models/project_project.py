# Copyright 2025 Miquel Pascual López(APSL-Nagarro)<mpascual@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.fields import Domain


class Project(models.Model):
    _inherit = "project.project"

    @api.depends("allow_timesheets", "timesheet_ids")
    def _compute_remaining_hours(self):
        res = super()._compute_remaining_hours()

        timesheets_read_group = self.env["account.analytic.line"]._read_group(
            Domain([("project_id", "in", self.ids), ("non_billable", "=", False)]),
            ["project_id"],
            ["unit_amount:sum"],
        )
        timesheet_time_dict = {
            project.id: unit_amount_sum
            for project, unit_amount_sum in timesheets_read_group
        }
        for project in self:
            project.remaining_hours = project.allocated_hours - timesheet_time_dict.get(
                project.id, 0
            )
            project.is_project_overtime = project.remaining_hours < 0

        return res
