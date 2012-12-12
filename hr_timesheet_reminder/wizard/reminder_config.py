# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Arnaud Wüst (Camptocamp)
#    Author: Guewen Baconnier (Camptocamp)
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

from osv import osv, fields


class reminder_config(osv.osv_memory):
    _name = 'hr.timesheet.reminder.config'

    _columns = {
        'reminder_active': fields.boolean('Reminder Active'),
        'interval_type': fields.selection([('days','Day(s)'), ('weeks', 'Week(s)'), ('months', 'Month(s)')],
                                           'Periodicity Unit',),
        'interval_number': fields.integer('Periodicity Quantity',),
        'nextcall': fields.datetime('Next Run',),
        'message': fields.text('Message', required=True),
        'subject': fields.char('Subject', size=200, required=True),
        'reply_to': fields.char('Reply To', size=100, required=True),
    }

    def _check_interval_number(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.interval_number < 1:
            return False
        return True

    _constraints = [
        (_check_interval_number, 'Periodicity must be greater than 0 ', ['interval_number']),
    ]

    def default_get(self, cr, uid, fields, context=None):
        res = super(reminder_config, self).default_get(cr, uid, fields, context=context)
        data = self.pool.get('hr.timesheet.reminder').\
        get_config(cr, uid, context)
        res.update(data)
        return res

    def run(self, cr, uid, ids, context):
        """ execute the timesheets check and send emails """
        reminder_obj = self.pool.get('hr.timesheet.reminder')
        reminder_obj.run(cr, uid, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def save(self, cr, uid, ids, context):
        """ save defined settings in db """

        # get the wizard datas
        wizard = self.browse(cr, uid, ids, context=context)[0]

        #retrieve the default cron values
        reminder_obj = self.pool.get('hr.timesheet.reminder')

        values = {}.fromkeys(wizard._columns.keys(), False)
        for field_name in values:
            values[field_name] = getattr(wizard, field_name)

        reminder_obj.save_config(cr, uid, False, values, context=context)
        return {'type': 'ir.actions.act_window_close'}

reminder_config()
