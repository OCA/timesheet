# Copyright 2025 Miquel Pascual López(APSL-Nagarro)<mpascual@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.depends("timesheet_ids.unit_amount")
    def _compute_effective_hours(self):
        res = super()._compute_effective_hours()

        for task in self:
            non_billable_hours = sum(
                timesheet.unit_amount
                for timesheet in task.timesheet_ids
                if timesheet.non_billable
            )
            task.effective_hours -= non_billable_hours

        return res
