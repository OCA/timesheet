# -*- coding: utf-8 -*-
# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    lead_id = fields.Many2one(comodel_name='crm.lead',
                              string='Lead/Opportunity')

    @api.onchange('account_id')
    def _onchange_account_id(self):
        if self.account_id:
            projects = self.env['project.project'].search([
                ('analytic_account_id', '=', self.account_id.id),
            ])
            if len(projects) == 1:
                self.project_id = projects
            elif not self.project_id < projects:
                self.project_id = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.account_id = self.project_id.analytic_account_id
