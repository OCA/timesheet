# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    timesheet_edit_level = fields.Selection(
        selection=[("none", "None"), ("approver", "Officer"), ("all", "All")],
        compute="_compute_timesheet_edit_level",
        store=True,
        readonly=False,
        default="none",
        help="""
        For this leave type, indicates who can edit generated timesheets
        """,
    )

    @api.depends("timesheet_generate", "timesheet_project_id")
    def _compute_timesheet_edit_level(self):
        self.filtered(
            lambda x: not (x.timesheet_generate and x.timesheet_project_id)
        ).timesheet_edit_level = "none"
