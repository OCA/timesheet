# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Guewen Baconnier (Camptocamp)
# Author : Arnaud Wüst (Camptocamp)
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

from osv import osv, fields


class ReminderConfig(osv.osv_memory):
    _name = 'hr.timesheet.reminder.config'

    _columns = {
        'reminder_active': fields.boolean('Reminder Active'),
        'interval_type': fields.selection(
            [('days', 'Day(s)'), ('weeks', 'Week(s)'), ('months', 'Month(s)')],
            'Periodicity Unit', ),
        'interval_number': fields.integer('Periodicity Quantity', ),
        'nextcall': fields.datetime('Next Run', ),
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
        (_check_interval_number, 'Periodicity must be greater than 0 ',
         ['interval_number']),
    ]

    def default_get(self, cr, uid, fields, context=None):
        res = super(ReminderConfig, self).default_get(cr, uid, fields,
                                                      context=context)
        data = self.pool.get('hr.timesheet.reminder'). \
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

        # retrieve the default cron values
        reminder_obj = self.pool.get('hr.timesheet.reminder')

        values = {}.fromkeys(wizard._columns.keys(), False)
        for field_name in values:
            values[field_name] = getattr(wizard, field_name)

        reminder_obj.save_config(cr, uid, False, values, context=context)
        return {'type': 'ir.actions.act_window_close'}


ReminderConfig()
