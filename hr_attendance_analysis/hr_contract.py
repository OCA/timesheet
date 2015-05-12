# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Stéphane Bidoul & Laetitia Gangloff
#    Copyright (c) 2013 Acsone SA/NV (http://www.acsone.eu)
#    Copyright (C) 2015 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import datetime
from openerp.osv import orm


class hr_contract(orm.Model):
    _inherit = 'hr.contract'

    def copy(self, cr, uid, contract_id, defaults, context=None):
        """ When duplicate a contract set the start date to the last end
        date + 1 day. If the last end date is False, do nothing"""
        contract = self.browse(cr, uid, contract_id, context=context)
        end_date_contract_id = self.search(
            cr, uid,
            [('employee_id', '=', contract.employee_id.id), ], limit=1,
            order='date_end desc', context=context)
        last_end_date = False
        if end_date_contract_id:
            contract = self.browse(
                cr, uid, end_date_contract_id, context=context)
            last_end_date = contract[0].date_end
        if last_end_date:
            defaults['date_start'] = datetime.datetime.strftime(
                datetime.datetime.strptime(last_end_date, "%Y-%m-%d") +
                datetime.timedelta(days=1), "%Y-%m-%d")
            defaults['date_end'] = False
            defaults['trial_date_start'] = False
            defaults['trial_date_end'] = False
        return super(hr_contract, self).copy(cr, uid, contract_id, defaults,
                                             context=context)
