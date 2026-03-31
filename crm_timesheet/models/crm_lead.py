# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmLead(models.Model):
    _name = "crm.lead"
    _inherit = ["crm.lead", "hr.timesheet.time_control.mixin"]

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        compute="_compute_project_id",
        store=True,
        readonly=False,
        ondelete="restrict",
        precompute=True,
    )
    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="lead_id",
        string="Timesheet",
    )
    total_time_spent = fields.Float(
        compute="_compute_total_time_spent",
        help="Total time spent on this lead/opportunity",
        store=True,
    )

    @api.depends("team_id")
    def _compute_project_id(self):
        for lead in self:
            if not lead.project_id:
                lead.project_id = lead.team_id.timesheet_project_id

    @api.depends("timesheet_ids.unit_amount")
    def _compute_total_time_spent(self):
        for lead in self:
            lead.total_time_spent = sum(lead.timesheet_ids.mapped("unit_amount"))

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
