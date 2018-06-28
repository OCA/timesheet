# -*- coding: utf-8 -*-
# Copyright 2015-18 Eficent Business and IT Consulting Services S.L.
#           (www.eficent.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('project_id')
    def _onchange_allowed_analytic_account_ids(self):
        """
        The purpose of the method is to define a domain for the available
        analytic accounts
        """
        result = {}
        if self.project_id:
            result['domain'] = {
                'project_id': [('allow_timesheets', '=', True)]}
        return result
