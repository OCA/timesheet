# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('is_timesheet')
    def _onchange_allowed_analytic_account_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        analytic accounts
        '''
        result = {}
        if self.is_timesheet:
            result['domain'] = {'account_id': [('use_timesheets', '=', True)]}
        return result
