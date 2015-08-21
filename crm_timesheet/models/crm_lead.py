# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from openerp import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account')
    timesheet_ids = fields.One2many(comodel_name='hr.analytic.timesheet',
                                    inverse_name='lead_id')
