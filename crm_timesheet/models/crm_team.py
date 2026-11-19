# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    timesheet_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Default Timesheet Project",
        domain=[("allow_timesheets", "=", True)],
        help="Default project to use for timesheets in leads of this team.",
    )
