# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def action_recompute_timesheet_cost(self):
        for aal in self.filtered('project_id'):
            if aal.employee_id.use_manual_timesheet_cost:
                cost = aal.employee_id.timesheet_cost_manual or 0.0
            else:
                cost = aal.employee_id.sudo()._get_timesheet_cost(aal.date)
            aal.amount = aal.employee_id.currency_id._convert(
                -aal.unit_amount * cost,
                aal.account_id.currency_id,
                aal.company_id,
                aal.date
            )
