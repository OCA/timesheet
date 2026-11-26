# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    show_timesheets_in_portal = fields.Boolean(
        string="Timesheets in Portal",
        default=True,
        help="Show the timesheets of this project and the time spent on its tasks "
        "to the portal users who have access to it.",
    )
