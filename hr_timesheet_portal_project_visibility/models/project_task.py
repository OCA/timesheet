# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    show_timesheets_in_portal = fields.Boolean(
        related="project_id.show_timesheets_in_portal",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS | {"show_timesheets_in_portal"}
