# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud WÃŒst
# Author: Guewen Baconnier
#
#
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
from report import report_sxw


class timesheet_status(report_sxw.rml_parse):
    _name = 'report.timesheet.reminder.status'

    def __init__(self, cr, uid, name, context):
        super(timesheet_status, self).__init__(cr, uid, name, context)
        self.data = {}
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
        return super(timesheet_status, self).set_context(objects, data, ids, report_type)

    def compute(self, objects):
        """compute all datas and do all the calculations before to start the rml rendering
           - objects are companies
        """
        #init the data array
        self.data = {}
        for o in objects:
            self.data[o.id] = {}
        #get the list of employees ids to treat
        for o in objects:
            self.data[o.id]['employees'] = self._compute_employees_list(o)

        #get the time range for each company
        for o in objects:
            self.data[o.id]['time_ranges'] = \
            self._compute_periods(o, time.strptime(self.end_date, "%Y-%m-%d"))

        #get the status of each timesheet for each employee
        for o in objects:
            self.data[o.id]['sheet_status'] = self._compute_all_status(o)

    def _compute_employees_list(self, company):
        """ return a dictionnary of lists of employees ids linked to the companies (param company) """
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(self.cr, self.uid,
                                           [('company_id', '=', company.id),
                                            ('active', '=', True)],
                                           context=self.localcontext)
        return employee_obj.browse(self.cr, self.uid, employee_ids, context=self.localcontext)

    def _get_last_period_dates(self, company, date):
        """ return the start date of the last period to display """
        return self.pool.get('res.company').\
        get_last_period_dates(self.cr, self.uid, company, date, context=self.localcontext)

    def _compute_periods(self, company, date):
        """ return the timeranges to display. This is the 5 last timesheets """
        return self.pool.get('res.company').\
        compute_timesheet_periods(self.cr, self.uid, company, date, context=self.localcontext)

    def get_title(self, obj):
        """ return the title of the main table """
        last_id = len(self.data[obj.id]['time_ranges']) - 1
        start_date = time.strptime(str(self.data[obj.id]['time_ranges'][last_id][0]),
                                   "%Y-%m-%d %H:%M:%S.00")
        start_date = time.strftime("%d.%m.%Y", start_date)

        end_date = time.strptime(str(self.data[obj.id]['time_ranges'][0][1]),
                                 "%Y-%m-%d %H:%M:%S.00")
        end_date = time.strftime("%d.%m.%Y", end_date)

        return obj.name + ", " + start_date + " to " + end_date

    def get_timerange_title(self, obj, cpt):
        """ return a header text for a periods column """
        start_date = self.data[obj.id]['time_ranges'][cpt][0]
        start_date = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S.00")
        start_date = time.strftime("%d.%m.%Y", start_date)

        end_date = self.data[obj.id]['time_ranges'][cpt][1]
        end_date = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S.00")
        end_date = time.strftime("%d.%m.%Y", end_date)

        return start_date + "\n " + end_date

    def get_user_list(self, obj):
        """ return the list of employees object ordered by name """
        return self.data[obj.id]['employees']

    def get_timesheet_status(self, obj, user, cpt):
        """ return the status to display for a user and a period """
        return self.data[obj.id]['sheet_status'][cpt][user.id]

    def _compute_timesheet_status(self, employee_id, period):
        """ return the timesheet status for a user and a period """
        return self.pool.get('hr.employee').\
        compute_timesheet_status(self.cr, self.uid, employee_id, period, context=self.localcontext)

    def _compute_all_status(self, o):
        """ compute all status for all employees for all periods """
        result = {}

        #for each periods
        for p_index in range(len(self.data[o.id]['time_ranges'])):
            result[p_index] = {}
            period = self.data[o.id]['time_ranges'][p_index]
            #for each employees
            for employee in self.data[o.id]['employees']:
                #compute the status
                result[p_index][employee.id] = self._compute_timesheet_status(employee.id, period)

        return result

report_sxw.report_sxw('report.timesheet.reminder.status', 'res.company',
                      'hr_timesheet_reminder/report/timesheet_status.rml',
                      parser=timesheet_status, header=False)
