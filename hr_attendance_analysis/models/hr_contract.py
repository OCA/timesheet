# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import datetime, timedelta
from openerp import models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def copy(self, default):
        """ When duplicate a contract set the start date to the last end
        date + 1 day. If the last end date is False, do nothing"""
        self.ensure_one()
        obj_contract = self.env["hr.contract"]
        contract = self[0]
        if default is None:
            default = {}

        end_date_contract = obj_contract.search(
            [('employee_id', '=', contract.employee_id.id), ], limit=1,
            order='date_end desc')
        if end_date_contract.date_end:
            default['date_start'] = datetime.strftime(
                datetime.strptime(
                    end_date_contract.date_end,
                    "%Y-%m-%d") +
                timedelta(days=1), "%Y-%m-%d")
            default['date_end'] = False
            default['trial_date_start'] = False
            default['trial_date_end'] = False
        return super(HrContract, self).copy(
            default)
