# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
from dateutil.relativedelta import relativedelta
from openerp import exceptions, fields
from openerp.tests.common import TransactionCase


class TestHrTimesheetPrintEmployeeTimesheet(TransactionCase):
    def test_hr_timesheet_print_employee_timesheet(self):
        wizard = self.env['hr.analytical.timesheet.employees']\
            .with_context(active_ids=self.env['hr.employee'].search([]).ids)\
            .create({})
        # demo data creates analytic lines for current months, the wizard by
        # default selects last month, we make the last month and this month
        wizard.date_end = fields.Date.to_string(
            fields.Date.from_string(wizard.date_end) +
            relativedelta(months=2, day=1, days=-1)
        )
        report = wizard.button_print()
        data, data_type = self.env['ir.actions.report.xml'].render_report(
            wizard.ids, report['report_name'], {})
        # check constraint
        with self.assertRaises(exceptions.ValidationError):
            self.env['hr.analytical.timesheet.employees'].with_context(
                active_ids=self.env['hr.employee'].search([]).ids
            ).create({
                'date_start': '2042-01-01',
                'date_end': '2018-01-01',
            })
