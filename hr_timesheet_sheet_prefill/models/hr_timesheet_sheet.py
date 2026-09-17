# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class Sheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    def action_prefill_from_previous(self):
        self.ensure_one()
        if self.state not in ("new", "draft"):
            raise UserError(_("You can only prefill a draft timesheet sheet."))
        previous_sheet = self.env["hr_timesheet.sheet"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("id", "!=", self.id),
                ("date_end", "<", self.date_start),
                ("state", "in", ("confirm", "done")),
            ],
            order="date_end desc",
            limit=1,
        )
        if not previous_sheet:
            raise UserError(
                _("No previous confirmed or approved timesheet sheet found.")
            )
        existing_keys = {(line.project_id, line.task_id) for line in self.timesheet_ids}
        unique_combos = {
            (line.project_id, line.task_id) for line in previous_sheet.timesheet_ids
        }
        lines_to_create = unique_combos - existing_keys
        if not lines_to_create:
            raise UserError(
                _(
                    "All project/task combinations from the previous period already "
                    "exist.",
                )
            )
        for project, task in lines_to_create:
            vals = self._prepare_empty_analytic_line(project=project, task=task)
            self.env["account.analytic.line"]._sheet_create(vals)
