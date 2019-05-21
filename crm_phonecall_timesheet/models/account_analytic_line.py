# Copyright 2015 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2015 Javier Iniesta <javieria@antiun.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    phonecall_id = fields.Many2one(comodel_name='crm.phonecall',
                                   string='Phone Call')
