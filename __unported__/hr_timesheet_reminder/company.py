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

from datetime import datetime
from dateutil.relativedelta import relativedelta, MO, SU
from openerp.osv import orm
from openerp.tools.translate import _


class ResCompany(orm.Model):
    _inherit = 'res.company'

    def get_reminder_recipients(self, cr, uid, ids, context=None):
        """Return the list of users that must receive the email"""
        res = dict((company_id, []) for company_id in ids)
        employee_obj = self.pool['hr.employee']
        for company in self.browse(cr, uid, ids, context=context):
            employee_ids = employee_obj.search(
                cr, uid, [('company_id', '=', company.id),
                          ('receive_timesheet_alerts', '=', True)],
                context=context)
            if not employee_ids:
                continue
            employees = employee_obj.browse(
                cr, uid, employee_ids, context=context)
            # periods
            periods = self.compute_timesheet_periods(
                cr, uid, company, datetime.now(), context=context)
            # remove the first one because it's the current one
            del periods[0]
            # for each employee
            for employee in employees:
                # is timesheet for a period not confirmed ?
                for period in periods:
                    status = employee_obj.compute_timesheet_status(
                        cr, uid, employee.id, period, context)
                    # if there is a missing sheet or a draft sheet
                    # and the user can receive alerts
                    # then we must alert the user
                    if status in ['Missing', 'Draft']:
                        res[company.id].append(employee)
                        # no need to go further for this user,
                        # he is now added in the list, go to the next one
                        break
        return res

    def compute_timesheet_periods(
            self, cr, uid, company, date, periods_number=5, context=None):
        """ return the timeranges to display. This is the 5 last timesheets"""
        periods = []
        last_start_date, last_end_date = self.get_last_period_dates(
            cr, uid, company, date, context=context)
        for cpt in range(periods_number):
            # find the delta between last_XXX_date to XXX_date
            if company.timesheet_range == 'month':
                delta = relativedelta(months=-cpt)
            elif company.timesheet_range == 'week':
                delta = relativedelta(weeks=-cpt)
            elif company.timesheet_range == 'year':
                delta = relativedelta(years=-cpt)
            else:
                raise orm.except_orm(
                    _('Error'),
                    _('Unknow timesheet range: %s') % company.timesheet_range)
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
