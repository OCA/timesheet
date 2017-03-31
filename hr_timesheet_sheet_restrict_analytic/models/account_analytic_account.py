# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    use_timesheets = fields.Boolean(deprecated=False, default=True,
                                    string="Use in Timesheets")
