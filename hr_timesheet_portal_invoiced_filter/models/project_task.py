# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    show_amount_due = fields.Boolean(compute="_compute_show_amount_due")

    def _compute_show_amount_due(self):
        for task in self:
            mode = (
                task.partner_id.commercial_partner_id._get_timesheet_portal_visibility()
            )
            has_open = any(not t.timesheet_invoice_id for t in task.timesheet_ids)
            task.show_amount_due = (mode == "all") or (not has_open)
