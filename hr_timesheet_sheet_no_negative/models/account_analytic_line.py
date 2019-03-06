# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _negative_unit_amount(self):
        if self._context.get('company_id'):
            company_id = self._context.get('company_id')
            company = self.env['res.company'].browse(company_id)
        else:
            company = self.company_id
        return company.timesheet_negative_unit_amount

    @api.onchange('unit_amount')
    def onchange_unit_amount(self):
        if not self._negative_unit_amount() and self.project_id \
                and self.unit_amount < 0.0:
            self.write({'unit_amount': 0.0})
