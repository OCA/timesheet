# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead", "hr.timesheet.time_control.mixin"]

    @api.depends("timesheet_ids.employee_id", "timesheet_ids.unit_amount")
    def _compute_show_time_control(self):
        return super()._compute_show_time_control()

    @api.model
    def _relation_with_timesheet_line(self):
        return "lead_id"

    def button_start_work(self):
        result = super().button_start_work()
        result["context"].update({"default_project_id": self.project_id.id})
        return result
