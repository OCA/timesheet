# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _timesheet_prepare_line_values(
        self, index, work_hours_data, day_date, work_hours_count, project, task
    ):
        timesheet_line = super()._timesheet_prepare_line_values(
            index, work_hours_data, day_date, work_hours_count, project, task
        )

        if self.company_id.dynamic_timesheet_description and self.name:
            old_ts_line = timesheet_line.get("name", "")
            timesheet_line["name"] = self.name + " - " + old_ts_line

        return timesheet_line
