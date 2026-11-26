# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.addons.hr_timesheet.controllers.project import ProjectCustomerPortal


class ProjectCustomerPortalVisibility(ProjectCustomerPortal):
    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        if not task.sudo().show_timesheets_in_portal:
            values["allow_timesheets"] = False
        return values
