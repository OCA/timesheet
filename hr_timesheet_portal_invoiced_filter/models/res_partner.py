# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    timesheet_portal_visibility = fields.Selection(
        [
            ("default", "Company default"),
            ("invoiced", "Invoiced only"),
            ("all", "All timesheets"),
        ],
        default="default",
    )

    def _get_timesheet_portal_visibility(self):
        self.ensure_one()
        commercial = self.commercial_partner_id
        value = commercial.timesheet_portal_visibility

        if value == "default":
            value = self.env.company.timesheet_portal_visibility

        return value
