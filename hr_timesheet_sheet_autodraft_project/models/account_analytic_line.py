# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def _get_autodraft_sheet_values(self):
        values = super()._get_autodraft_sheet_values()
        if self.company_id.timesheet_sheet_review_policy == 'project_manager':
            values.update({
                'project_id': self.project_id.id,
            })
        return values
