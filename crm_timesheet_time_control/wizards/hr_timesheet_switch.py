# Copyright 2019 Tecnativa - Jairo Llopis
# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    name = fields.Char(required=False)

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if "project_id" in fields_list and not result.get("project_id"):
            context = self.env.context
            lead_id = context.get("default_lead_id") or (
                context.get("active_model") == "crm.lead" and context.get("active_id")
            )
            if lead_id:
                lead = self.env["crm.lead"].browse(lead_id)
                if lead.project_id:
                    result["project_id"] = lead.project_id.id
        return result

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
