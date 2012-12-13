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

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    _columns = {
        'receive_timesheet_alerts': fields.boolean('Receive Timesheet Alerts'),
    }

    _defaults = {
        'receive_timesheet_alerts': True,
    }

    def compute_timesheet_status(self, cr, uid, ids, period, context):
        """ return the timesheet status for an employee
         from its id and a period (tuple from date-to date)"""
        status = 'Error'

        if isinstance(ids, list):
            assert len(ids) == 1, "Only 1 ID expected"
            ids = ids[0]

        employee = self.browse(cr, uid, ids, context=context)

        time_from, time_to = period

        # does the timesheet exists in db and what is its status?
        str_date_from = time_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        str_date_to = time_to.strftime(DEFAULT_SERVER_DATE_FORMAT)

        cr.execute(
            """SELECT state, date_from, date_to
               FROM hr_timesheet_sheet_sheet
               WHERE employee_id = %s
               AND date_from >= %s
               AND date_to <= %s""",
            (employee.id, str_date_from, str_date_to))
        sheets = cr.dictfetchall()

        # the timesheet does not exists in db
        if not sheets:
            status = 'Missing'

        else:
            status = 'Confirmed'
            for sheet in sheets:
                if sheet['state'] == 'draft':
                    status = 'Draft'
        return status
