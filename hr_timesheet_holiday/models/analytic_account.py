# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AnalyticAccount(models.Model):
    """Add 'is leave account' flag to Analytic Account"""
    _inherit = 'account.analytic.account'

    is_leave_account = fields.Boolean(
        'Leaves',
        help="Check this field if this account manages leaves",
        default=False,
    )
    holiday_status_ids = fields.One2many(
        'hr.holidays.status',
        'analytic_account_id',
    )
