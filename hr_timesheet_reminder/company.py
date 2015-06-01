# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Arnaud Wüst (Camptocamp)
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


from datetime import date, datetime
from dateutil.relativedelta import *
from osv import fields, osv
from tools.translate import _


class ResCompany(osv.osv):
    _inherit = 'res.company'

    def get_reminder_recipients(self, cr, uid, ids, context=None):
        """Return the list of users that must receive the email"""
        res = dict((company_id, []) for company_id in ids)

        employee_obj = self.pool.get('hr.employee')

        for company in self.browse(cr, uid, ids, context=context):
            employee_ids = employee_obj.search(
                cr, uid,
                [('company_id', '=', company.id),
                 ('active', '=', True)],
                context=context)
            employees = employee_obj.browse(cr, uid, employee_ids, context=context)

            # periods
            periods = self.compute_timesheet_periods(cr, uid, company, datetime.now(), context=context)
            # remove the first one because it's the current one
            del periods[0]

            # for each employee
            for employee in employees:
                # is timesheet for a period not confirmed ?
                for p_index in range(len(periods)):
                    period = periods[p_index]
                    status = employee_obj.compute_timesheet_status(cr, uid, employee.id, period, context)

                    # if there is a missing sheet or a draft sheet
                    # and the user can receive alerts
                    # then we must alert the user
                    if status in ['Missing', 'Draft'] and employee.receive_timesheet_alerts:
                        res[company.id].append(employee)
                        break  # no need to go further for this user, he is now added in the list, go to the next one
        return res

    def compute_timesheet_periods(self, cr, uid, company, date, periods_number=5, context=None):
        """ return the timeranges to display. This is the 5 last timesheets"""
        periods = []
        last_start_date, last_end_date = self.get_last_period_dates(cr, uid, company, date, context=context)
        for cpt in range(periods_number):
            # find the delta between last_XXX_date to XXX_date
            if company.timesheet_range == 'month':
                delta = relativedelta(months=-cpt)
            elif company.timesheet_range == 'week':
                delta = relativedelta(weeks=-cpt)
            elif company.timesheet_range == 'year':
                delta = relativedelta(years=-cpt)
            else:
                raise osv.except_osv(_('Error'), _('Unknow timesheet range: %s') % (company.timesheet_range,))

            start_date = last_start_date + delta
            end_date = last_end_date + delta
            periods.append((start_date, end_date))

        return periods

    def get_last_period_dates(self, cr, uid, company, date, context=None):
        """ return the start date and end date of the last period to display """
        
        # return the first day and last day of the month
        if company.timesheet_range == 'month':
            start_date = date
            end_date = start_date + relativedelta(months=+1)

        # return the first and last days of the week
        elif company.timesheet_range == 'week':
            # get monday of current week
            start_date = date + relativedelta(weekday=MO(-1))
            # get sunday of current week 
            end_date = date + relativedelta(weekday=SU(+1))

        # return the first and last days of the year
        else:
            start_date = datetime(date.year, 1, 1) 
            end_date = datetime(date.year, 12, 31)

        return start_date, end_date


ResCompany()
