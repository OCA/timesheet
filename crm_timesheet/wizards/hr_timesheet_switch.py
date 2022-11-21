# Copyright 2019 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    @api.model
    def _closest_suggestion(self):
        """Allow searching best suggestion by lead."""
        context = self.env.context
        if context.get("active_model") == "crm.lead":
            return self.env["account.analytic.line"].search(
                [
                    ("employee_id", "in", self.env.user.employee_ids.ids),
                    ("lead_id", "=", context.get("active_id", 0)),
                ],
                order="date_time DESC",
                limit=1,
            )
        return super()._closest_suggestion()
