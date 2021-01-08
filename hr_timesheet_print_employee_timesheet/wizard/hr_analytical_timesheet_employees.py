# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
import collections
import datetime
import babel.dates
from dateutil.relativedelta import relativedelta
from openerp import _, models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import ValidationError


class HrAnalyticalTimesheetEmployees(models.TransientModel):
    _name = 'hr.analytical.timesheet.employees'
    _description = 'Print timesheets per employee'

    employee_ids = fields.Many2many(
        'hr.employee', string='Employees',
        default=lambda self: self.env.context.get('active_ids', []),
        required=True)
    date_start = fields.Date(
        'Start date',
        default=lambda self: (
            datetime.date.today() + relativedelta(day=1, months=-1)
        ).strftime(DEFAULT_SERVER_DATE_FORMAT),
        help='This will be normalized to the beginning of a month',
        required=True)
    date_end = fields.Date(
        'End date',
        default=lambda self: (
            datetime.date.today() + relativedelta(day=1, days=-1)
        ).strftime(DEFAULT_SERVER_DATE_FORMAT),
        help='This will be normalized to the end of a month',
        required=True)
    short_account_names = fields.Boolean(
        'Short account names', help='This will show only the analytic '
        'account\'s name, not the hierarchy')

    @api.multi
    def button_print(self):
        return self.env['report'].with_context(landscape=True).get_action(
            self,
            'hr_timesheet_print_employee_timesheet.'
            'qweb_hr_analytical_timesheet_employees')

    @api.multi
    def get_timesheets(self, employee):
        self.ensure_one()
        rows = self.env['hr.analytic.timesheet']\
            .with_context(hr_timesheet_print_employee_timesheet_date_raw=True)\
            .read_group(
                [
                    ('date', '>=', self.date_start),
                    ('date', '<=', self.date_end),
                    ('user_id', '=', employee.user_id.id),
                ],
                ['date', 'account_id', 'unit_amount'],
                ['date:day', 'account_id'],
                lazy=False)

        date = fields.Date.from_string(self.date_start)
        date_end = fields.Date.from_string(self.date_end)

        result = []
        timesheet_per_day = {}
        current_timesheet = collections.OrderedDict()
        current_timesheet.accounts = self.env['account.analytic.account']\
            .browse([])
        current_timesheet.date_start = date

        while date <= date_end:
            if date.month != current_timesheet.date_start.month:
                result.append(current_timesheet)
                current_timesheet = collections.OrderedDict()
                current_timesheet.accounts = self\
                    .env['account.analytic.account'].browse([])
                current_timesheet.date_start = date
            timesheet_per_day[date] = current_timesheet
            current_timesheet.setdefault(date, {})
            date += datetime.timedelta(days=1)

        if current_timesheet not in result:
            result.append(current_timesheet)

        for row in rows:
            date = row['date:raw'].date()
            current_timesheet = timesheet_per_day[date]
            hours = current_timesheet[date]
            account_id = row['account_id'][0]
            hours[account_id] = row['unit_amount']
            if account_id not in current_timesheet.accounts.ids:
                current_timesheet.accounts += self\
                    .env['account.analytic.account'].browse([account_id])

        return result

    @api.model
    def format_date(self, date, fmt):
        return babel.dates.format_date(
            date, format=fmt, locale=self.env.context.get('lang', 'en_US'))

    @api.constrains('date_start', 'date_end')
    def _constrain_dates(self):
        for this in self:
            if this.date_start > this.date_end:
                raise ValidationError(
                    _('Start date must be greater than end date')
                )
