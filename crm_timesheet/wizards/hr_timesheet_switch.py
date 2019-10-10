# Copyright 2019 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    @api.model
    def _closest_suggestion(self):
        """Allow searching best suggestion by lead."""
        result = super()._closest_suggestion()
        try:
            if not result and self.env.context["active_model"] == "crm.lead":
                return self.env["account.analytic.line"].search(
                    [
                        ("employee_id", "in", self.env.user.employee_ids.ids),
                        ("lead_id", "=", self.env.context["active_id"]),
                    ],
                    order="date_time DESC",
                    limit=1,
                )
        except KeyError:
            # If I don't know where's the user, I don't know what to suggest
            pass
        return result
