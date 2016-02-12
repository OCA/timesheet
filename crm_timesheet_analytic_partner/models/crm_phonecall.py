# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    def _timesheet_prepare(self, vals):
        res = super(CrmPhonecall, self)._timesheet_prepare(vals)
        if vals.get('partner_id'):
            res['other_partner_id'] = vals.get('partner_id')
        return res
