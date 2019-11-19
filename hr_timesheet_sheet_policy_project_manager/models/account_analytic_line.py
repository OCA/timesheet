# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _get_sheet_domain(self):
        domain = super()._get_sheet_domain()
        if self.company_id.timesheet_sheet_review_policy == 'project_manager':
            domain += [
                ('project_id', '=', self.project_id.id),
            ]
        return domain
