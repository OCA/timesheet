# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class HrHolidaysStatus(models.Model):
    """Add analytic account to holiday status"""
    _inherit = 'hr.holidays.status'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account'
    )
