# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from openerp import models, fields


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    lead_id = fields.Many2one(string='Lead/Opportunity',
                              comodel_name='crm.lead')
    phonecall_id = fields.Many2one(string='Phone Call',
                                   comodel_name='crm.phonecall')
