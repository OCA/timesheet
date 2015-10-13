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

import time
from datetime import datetime
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class timesheet_status(report_sxw.rml_parse):
    _name = 'report.timesheet.reminder.status'

    def __init__(self, cr, uid, name, context=None):
        super(timesheet_status, self).__init__(cr, uid, name, context=context)
        self.data = {}
        self.end_date = None
        self.localcontext.update({
            'compute': self.compute,
            'time': time,
            'get_title': self.get_title,
            'get_timerange_title': self.get_timerange_title,
            'get_user_list': self.get_user_list,
            'get_timesheet_status': self.get_timesheet_status,
        })

    def set_context(self, objects, data, ids, report_type=None):
        self.end_date = data['form']['date']
        self.compute(objects)
        return super(timesheet_status, self).set_context(
            objects, data, ids, report_type)

    def compute(self, objects):
        """compute all datas and do all the calculations before to start the rml
        rendering
        - objects are companies
        """
        # init the data array
        self.data = {}
        for o in objects:
            self.data[o.id] = {}
        # get the list of employees ids to treat
        for o in objects:
            self.data[o.id]['employees'] = self._compute_employees_list(o)
        # get the time range for each company
        end_date = datetime.strptime(self.end_date, DEFAULT_SERVER_DATE_FORMAT)
        for o in objects:
            self.data[o.id]['time_ranges'] = self._compute_periods(o, end_date)
        # get the status of each timesheet for each employee
        for o in objects:
            self.data[o.id]['sheet_status'] = self._compute_all_status(o)

    def _compute_employees_list(self, company):
        """ return a dictionnary of lists of employees ids linked
        to the companies (param company) """
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(self.cr, self.uid,
                                           [('company_id', '=', company.id),
                                            ('active', '=', True)],
                                           context=self.localcontext)
        return employee_obj.browse(
            self.cr, self.uid, employee_ids, context=self.localcontext)

    def _get_last_period_dates(self, company, date):
        """ return the start date of the last period to display """
        return self.pool['res.company'].get_last_period_dates(
            self.cr, self.uid, company, date, context=self.localcontext)

    def _compute_periods(self, company, date):
        """ return the timeranges to display. This is the 5 last timesheets """
        return self.pool['res.company'].compute_timesheet_periods(
            self.cr, self.uid, company, date, context=self.localcontext)

    def get_title(self, obj):
        """ return the title of the main table """
        timerange = self.data[obj.id]['time_ranges']
        start_date = self.formatLang(timerange[-1][0], date=True)
        end_date = self.formatLang(timerange[0][1], date=True)
        return obj.name + ", " + start_date + _(" to ") + end_date

    def get_timerange_title(self, obj, cpt):
        """ return a header text for a periods column """
        timerange = self.data[obj.id]['time_ranges'][cpt]
        start_date = self.formatLang(timerange[0], date=True)
        end_date = self.formatLang(timerange[1], date=True)
        return start_date + "\n " + end_date

    def get_user_list(self, obj):
        """ return the list of employees object ordered by name """
        return self.data[obj.id]['employees']

    def get_timesheet_status(self, obj, user, cpt):
        """ return the status to display for a user and a period """
        return self.data[obj.id]['sheet_status'][cpt][user.id]

    def _compute_timesheet_status(self, employee_id, period):
        """ return the timesheet status for a user and a period """
        return self.pool['hr.employee'].compute_timesheet_status(
            self.cr, self.uid, employee_id, period, context=self.localcontext)

    def _compute_all_status(self, obj):
        """ compute all status for all employees for all periods """
        result = {}
        # for each periods
        for p_index, period in enumerate(self.data[obj.id]['time_ranges']):
            result[p_index] = {}
            # for each employees
            for employee in self.data[obj.id]['employees']:
                # compute the status
                result[p_index][employee.id] = self._compute_timesheet_status(
                    employee.id, period)
        return result

report_sxw.report_sxw('report.timesheet.reminder.status', 'res.company',
                      'hr_timesheet_reminder/report/timesheet_status.rml',
                      parser=timesheet_status, header=False)
