# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Arnaud Wüst (Camptocamp)
#    Author: Guewen Baconnier (Camptocamp) (port to v7)
#    Copyright 2011-2012 Camptocamp SA
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

from openerp.osv import orm, fields


class ReminderStatus(orm.TransientModel):
    _name = 'hr.timesheet.reminder.status'

    _columns = {
        'company_ids': fields.many2many(
            'res.company',
            'reminder_company_rel',
            'wid',
            'rid',
            string='Company'),
        'date': fields.date('End Date', required=True),
    }

    _defaults = {
        'date': lambda *a: fields.date.today(),
    }

    def print_report(self, cr, uid, ids, context=None):
        form_values = self.read(
            cr, uid, ids[0], ['company_ids', 'date'], context=context)
        # when no company is selected, select them all
        if not form_values['company_ids']:
            form_values['company_ids'] = self.pool['res.company'].search(
                cr, uid, [], context=context)
        data = {'ids': form_values['company_ids'],
                'model': 'res.company',
                'form': form_values}
        return {'type': 'ir.actions.report.xml',
                'report_name': 'timesheet.reminder.status',
                'datas': data}
