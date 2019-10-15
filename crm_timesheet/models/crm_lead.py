# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', "hr.timesheet.time_control.mixin"]

    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project",
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='lead_id',
        string="Timesheet",
    )

    @api.model
    def _relation_with_timesheet_line(self):
        return "lead_id"

    @api.depends("timesheet_ids.employee_id", "timesheet_ids.unit_amount")
    def _compute_show_time_control(self):
        return super()._compute_show_time_control()

    def button_start_work(self):
        result = super().button_start_work()
        result["context"].update({
            "default_project_id": self.project_id.id,
        })
        return result
