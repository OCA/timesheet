# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    lead_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Lead/Opportunity",
    )

    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        if self.lead_id.project_id:
            self.project_id = self.lead_id.project_id.id

    def button_end_work(self):
        if self.env.context.get("skip_stop_wizard"):
            return super().button_end_work()

        # If it's a CRM lead timer, ask for description
        # We only do this if it's a single line being stopped
        if len(self) == 1 and self.lead_id:
            return {
                "name": self.env._("Stop Work"),
                "type": "ir.actions.act_window",
                "res_model": "hr.timesheet.stop",
                "view_mode": "form",
                "view_id": self.env.ref("crm_timesheet.hr_timesheet_stop_view_form").id,
                "target": "new",
                "context": {
                    "default_analytic_line_id": self.id,
                    "default_name": self.name,
                },
            }
        return super().button_end_work()
