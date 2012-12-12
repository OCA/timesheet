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


import tools
import time

from datetime import datetime, timedelta
from osv import fields, osv
from tools.translate import _

class reminder(osv.osv):
    _name = "hr.timesheet.reminder"
    _description = "Handle the scheduling of timesheet reminders"

    _columns = {
            'reply_to': fields.char('Reply To', size=100),
            'message': fields.text('Message'),
            'subject': fields.char('Subject', size=200),
    }

    #default cron (the one created if missing)
    cron = {'active': False,
            'priority': 1,
            'interval_number': 1,
            'interval_type': 'weeks',
            'nextcall': time.strftime("%Y-%m-%d %H:%M:%S",
                                      (datetime.today()
                                       + timedelta(days=1)).timetuple()),  # tomorrow same time
            'numbercall': -1,
            'doall': True,
            'model': 'hr.timesheet.reminder',
            'function': 'run',
            'args': '()',
            }

    #default message (the one created if missing)
    message = {'reply_to': 'spam@camptocamp.com'}

    def run(self, cr, uid, context=None):
        """ find the reminder recipients and send them an email """
        context = context or {}

        company_obj = self.pool.get('res.company')
        #get all companies
        company_ids = company_obj.search(cr, uid, [], context=context)

        #for each company, get all recipients
        recipients = []
        company_recipients = company_obj.get_reminder_recipients(cr, uid, company_ids, context=context)
        for company_id, rec in company_recipients.iteritems():
            recipients += rec

        #get the message to send
        message_id = self.get_message_id(cr, uid, context)
        message_data = self.browse(cr, uid, message_id, context=context)

        #send them email if they have an email defined
        emails = []
        for employee in recipients:
            if employee.work_email:
                emails.append(employee.work_email)

        if emails:
            tools.email_send(message_data.reply_to, [], message_data.subject, message_data.message, email_bcc=emails)

    def get_cron_id(self, cr, uid, context):
        """return the reminder cron's id. Create one if the cron does not exists """
        cron_obj = self.pool.get('ir.cron')
        # find the cron that send messages
        cron_id = cron_obj.search(cr, uid,  [('function', 'ilike', self.cron['function']),
                                             ('model', 'ilike', self.cron['model'])],
                                  context={'active_test': False})
        if cron_id:
            cron_id = cron_id[0]

        # the cron does not exists
        if not cron_id:
            self.cron['name'] = _('timesheet status reminder')
            cron_id = cron_obj.create(cr, uid, self.cron, context)

        return cron_id

    def get_message_id(self, cr, uid, context):
        """ return the message'id. create one if the message does not exists """
        #there is only one line in db, let's get it
        message_id = self.search(cr, uid, [], limit=1, context=context)

        if message_id:
            message_id = message_id[0]

        #the message does not exists
        if not message_id:
            #translate
            self.message['subject'] = _('Timesheet Reminder')
            self.message['message'] = _('At least one of your last timesheets is still in draft or is missing. Please take time to complete and confirm it.')

            message_id = self.create(cr, uid, self.message, context)

        return message_id

    def get_config(self, cr, uid, context):
        """return the reminder config from the db """

        cron_id = self.get_cron_id(cr, uid, context)

        cron_data = self.pool.get('ir.cron').browse(cr, uid, cron_id)

        #there is only one line in db, let's get it
        message_id = self.get_message_id(cr, uid, context)
        message_data = self.browse(cr, uid, message_id)
        return {'reminder_active': cron_data.active,
                'interval_type': cron_data.interval_type,
                'interval_number': cron_data.interval_number,
                'reply_to': message_data.reply_to,
                'message':  message_data.message,
                'subject': message_data.subject,
                'nextcall': cron_data.nextcall,
               }

    def save_config(self, cr, uid, ids, datas, context):
        """save the reminder config """

        #modify the cron
        cron_id = self.get_cron_id(cr, uid, context)
        self.pool.get('ir.cron').write(cr, uid, [cron_id],
                {'active': datas['reminder_active'],
                 'interval_number': datas['interval_number'],
                 'interval_type': datas['interval_type'],
                 'nextcall': datas['nextcall'], },
                 context=context)
        #modify the message
        message_id = ids or self.get_message_id(cr, uid, context)
        self.write(cr, uid, [message_id],
                {'reply_to': datas['reply_to'],
                 'message': datas['message'],
                 'subject': datas['subject'],
                }, context=context)
        return True

reminder()
