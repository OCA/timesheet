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

from datetime import datetime, timedelta
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Reminder(orm.Model):
    _name = "hr.timesheet.reminder"
    _description = "Handle the scheduling of timesheet reminders"

    _columns = {
        'reply_to': fields.char('Reply To'),
        'message': fields.html('Message'),
        'subject': fields.char('Subject'),
    }

    # default cron (the one created if missing)
    cron = {'active': False,
            'priority': 1,
            'interval_number': 1,
            'interval_type': 'weeks',
            'nextcall': False,  # to set on the creation of the cron
            'numbercall': -1,
            'doall': False,
            'model': 'hr.timesheet.reminder',
            'function': 'run',
            'args': '()',
            }

    # default message (the one created if missing)
    message = {'reply_to': 'spam@camptocamp.com'}

    def run(self, cr, uid, context=None):
        """ find the reminder recipients and send them an email """
        company_obj = self.pool.get('res.company')
        # get all companies
        company_ids = company_obj.search(cr, uid, [], context=context)
        # for each company, get all recipients
        recipients = []
        company_recipients = company_obj.get_reminder_recipients(
            cr, uid, company_ids, context=context)
        for rec in company_recipients.itervalues():
            recipients += rec
        # get the message to send
        message_id = self.get_message_id(cr, uid, context)
        message_data = self.browse(cr, uid, message_id, context=context)
        # send them email if they have an email defined
        for employee in recipients:
            if not employee.work_email:
                continue
            vals = {
                'state': 'outgoing',
                'subject': message_data.subject,
                'body_html': message_data.message,
                'email_to': employee.work_email,
                'email_from': message_data.reply_to,
            }
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)

        return True

    def get_cron_id(self, cr, uid, context=None):
        """return the reminder cron's id. Create one if the cron does not
        exists
        """
        if context is None:
            context = {}
        cron_obj = self.pool['ir.cron']
        # find the cron that send messages
        ctx = dict(context, active_test=False)
        cron_ids = cron_obj.search(
            cr, uid,
            [('function', 'ilike', self.cron['function']),
             ('model', 'ilike', self.cron['model'])],
            context=ctx)
        cron_id = None
        if cron_ids:
            cron_id = cron_ids[0]
        # the cron does not exists
        if cron_id is None:
            vals = dict(self.cron, name=_('timesheet status reminder'),
                        nextcall=self._cron_nextcall())
            cron_id = cron_obj.create(cr, uid, vals, context=context)
        return cron_id

    @staticmethod
    def _cron_nextcall():
        tomorrow = datetime.today() + timedelta(days=1)
        return tomorrow.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_message_id(self, cr, uid, context=None):
        """ return the message's id. create one if the message does not
        exists
        """
        # there is only one line in db, let's get it
        message_ids = self.search(cr, uid, [], limit=1, context=context)
        message_id = message_ids and message_ids[0] or None
        # the message does not exists
        if message_id is None:
            vals = dict(
                self.message, subject=_('Timesheet Reminder'),
                message=_('At least one of your last timesheets is still '
                          'in draft or is missing. Please take time to '
                          'complete and confirm it.'))
            message_id = self.create(cr, uid, vals, context)
        return message_id

    def get_config(self, cr, uid, context=None):
        """return the reminder config from the db """
        cron_id = self.get_cron_id(cr, uid, context)
        cron_data = self.pool['ir.cron'].browse(
            cr, uid, cron_id, context=context)
        # there is only one line in db, let's get it
        message_id = self.get_message_id(cr, uid, context=context)
        message_data = self.browse(cr, uid, message_id, context=context)
        return {'reminder_active': cron_data.active,
                'interval_type': cron_data.interval_type,
                'interval_number': cron_data.interval_number,
                'reply_to': message_data.reply_to,
                'message': message_data.message,
                'subject': message_data.subject,
                'nextcall': self._cron_nextcall(),
                }

    def save_config(self, cr, uid, ids, datas, context=None):
        """save the reminder config """
        # modify the cron
        cron_id = self.get_cron_id(cr, uid, context=context)
        self.pool['ir.cron'].write(
            cr, uid, [cron_id],
            {'active': datas['reminder_active'],
             'interval_number': datas['interval_number'],
             'interval_type': datas['interval_type'],
             'nextcall': datas['nextcall'], },
            context=context)
        # modify the message
        message_id = ids or self.get_message_id(cr, uid, context)
        self.write(
            cr, uid, [message_id],
            {'reply_to': datas['reply_to'],
             'message': datas['message'],
             'subject': datas['subject'],
             }, context=context)
        return True
