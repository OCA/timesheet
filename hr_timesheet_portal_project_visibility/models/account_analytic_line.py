# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import models
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_get_portal_domain(self):
        domain = super()._timesheet_get_portal_domain()
        if not self.env.user.share:
            return domain
        return expression.AND(
            [
                domain,
                [
                    "|",
                    ("project_id.show_timesheets_in_portal", "=", True),
                    ("user_id", "=", self.env.uid),
                ],
            ]
        )
