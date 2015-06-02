# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Guewen Baconnier (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time

from openerp.osv import osv, fields


class ReminderStatus(osv.osv_memory):
    _name = 'hr.timesheet.reminder.status'

    _columns = {
        'company_ids': fields.many2many('res.company', 'reminder_company_rel',
                                        'wid', 'rid', 'Company'),
        'date': fields.date('End Date', required=True),
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def print_report(self, cr, uid, ids, context):
        if context is None:
            context = {}

        form_values = self.read(cr, uid, ids, ['company_ids', 'date'])[0]

        if not form_values['company_ids']:
            form_values['company_ids'] = self.pool.get('res.company'). \
                search(cr, uid, [], context=context)
        data = {'ids': form_values['company_ids'],
                'model': 'res.company',
                'form': {}}
        data['form'].update(form_values)

        return {'type': 'ir.actions.report.xml',
                'report_name': 'timesheet.reminder.status',
                'datas': data}
