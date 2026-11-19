# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.fields import Domain


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_get_portal_domain(self):
        domain = super()._timesheet_get_portal_domain()
        if self.env.user.has_group("hr_timesheet.group_hr_timesheet_user"):
            return domain

        partner = (
            self.env.user.partner_id.commercial_partner_id
            if self.env.user.partner_id
            else None
        )
        if partner and partner._get_timesheet_portal_visibility() == "invoiced":
            domain = Domain.AND([domain, [("timesheet_invoice_id", "!=", False)]])

        return domain
