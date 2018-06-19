# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Lead/Opportunity',
    )

    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        if self.lead_id.project_id:
            self.project_id = self.lead_id.project_id.id
