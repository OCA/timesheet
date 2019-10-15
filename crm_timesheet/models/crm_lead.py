# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project",
    )
    show_time_control = fields.Selection(
        selection=[("start", "Start"), ("stop", "Stop")],
        compute="_compute_show_time_control",
        help="Indicate which time control button to show, if any.",
    )
    timesheet_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='lead_id',
        string="Timesheet",
    )

    @api.model
    def _timesheet_running_domain(self):
        """Domain to find running timesheet lines."""
        return self.env["account.analytic.line"]._running_domain() + [
            ("lead_id", "in", self.ids),
        ]

    @api.depends("timesheet_ids.employee_id", "timesheet_ids.unit_amount")
    def _compute_show_time_control(self):
        """Decide which time control button to show, if any."""
        grouped = self.env["account.analytic.line"].read_group(
            domain=self._timesheet_running_domain(),
            fields=["id"],
            groupby=["lead_id"],
        )
        lines_per_lead = {group["lead_id"][0]: group["lead_id_count"]
                          for group in grouped}
        button_per_lines = {0: "start", 1: "stop"}
        for lead in self:
            lead.show_time_control = button_per_lines.get(
                lines_per_lead.get(lead.id, 0),
                False,
            )

    def button_start_work(self):
        """Create a new record starting now, with a running timer."""
        return {
            "context": {
                "default_project_id": self.project_id.id,
                "default_lead_id": self.id,
            },
            "name": _("Start work"),
            "res_model": "hr.timesheet.switch",
            "target": "new",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
        }

    @api.multi
    def button_end_work(self):
        running_lines = self.env["account.analytic.line"].search(
            self._timesheet_running_domain(),
        )
        if not running_lines:
            raise UserError(
                _("No running timer found in lead/opportunity %s. "
                  "Refresh the page and check again.") % self.display_name,
            )
        return running_lines.button_end_work()
