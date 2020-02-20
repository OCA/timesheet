# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import fields
from odoo.tests import common


class TestHrTimesheetEmployeeCostContract(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.HrEmployee = self.env['hr.employee']
        self.ResourceCalendarLeave = self.env['resource.calendar.leaves']
        self.today = fields.Date.today()
        self.eur = self.env.ref('base.EUR')

    def test_defaults(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'timesheet_cost': 42.0,
        })

        self.assertEqual(employee.use_manual_timesheet_cost, True)
        self.assertEqual(employee.timesheet_cost, 42.0)

    def test_manual(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'timesheet_cost_manual': 42.0,
            'use_manual_timesheet_cost': False,
        })

        self.assertEqual(employee.timesheet_cost, 0.0)

        employee.use_manual_timesheet_cost = True
        self.assertEqual(employee.timesheet_cost, 42.0)

        employee.timesheet_cost = 1.0
        self.assertEqual(employee.timesheet_cost_manual, 1.0)

    def test_contracts(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'use_manual_timesheet_cost': False,
            'contract_ids': [
                (0, 0, {
                    'name': 'Employee Contract #1',
                    'wage': 3000.0,
                    'state': 'open',
                    'date_start': self.today - relativedelta(years=1),
                    'date_end': self.today + relativedelta(years=1),
                }),
                (0, 0, {
                    'name': 'Employee Contract #2',
                    'wage': 1000.0,
                    'state': 'open',
                    'date_start': self.today - relativedelta(years=1),
                }),
            ],
        })
        self.assertEqual(employee.use_manual_timesheet_cost, False)
        self.assertGreater(employee.timesheet_cost, 0)

    def test_contract_avg(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'use_manual_timesheet_cost': False,
            'contract_ids': [
                (0, 0, {
                    'name': 'Employee Contract #1',
                    'wage': 3000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
                (0, 0, {
                    'name': 'Employee Contract #2',
                    'wage': 1000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
            ],
        })
        as_of_day = date(2020, 12, 31)
        contracts = employee._get_timesheet_cost_contracts(as_of_day)
        self.assertEqual(len(contracts), 2)
        average_hourly_cost = contracts._compute_average_hourly_cost(
            'contract_avg',
            self.eur,
            as_of_day
        )
        self.assertEqual(average_hourly_cost, 7.50)

    def test_annual_avg(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'use_manual_timesheet_cost': False,
            'contract_ids': [
                (0, 0, {
                    'name': 'Employee Contract #1',
                    'wage': 3000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
                (0, 0, {
                    'name': 'Employee Contract #2',
                    'wage': 1000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
            ],
        })
        as_of_day = date(2020, 12, 1)
        contracts = employee._get_timesheet_cost_contracts(as_of_day)
        self.assertEqual(len(contracts), 2)
        average_hourly_cost = contracts._compute_average_hourly_cost(
            'annual_avg',
            self.eur,
            as_of_day
        )
        self.assertEqual(average_hourly_cost, 7.53)

    def test_monthly_avg(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'use_manual_timesheet_cost': False,
            'contract_ids': [
                (0, 0, {
                    'name': 'Employee Contract #1',
                    'wage': 3000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
                (0, 0, {
                    'name': 'Employee Contract #2',
                    'wage': 1000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
            ],
        })
        as_of_day = date(2020, 1, 1)
        contracts = employee._get_timesheet_cost_contracts(as_of_day)
        self.assertEqual(len(contracts), 2)
        average_hourly_cost = contracts._compute_average_hourly_cost(
            'annual_avg',
            self.eur,
            as_of_day
        )
        self.assertEqual(average_hourly_cost, 8.94)

    def test_leaves(self):
        employee = self.HrEmployee.create({
            'name': 'Employee',
            'use_manual_timesheet_cost': False,
            'contract_ids': [
                (0, 0, {
                    'name': 'Employee Contract #1',
                    'wage': 1000.0,
                    'state': 'open',
                    'date_start': date(2020, 1, 1),
                }),
            ],
        })
        tz = timezone(employee.tz)
        as_of_day = date(2020, 1, 31)

        self.assertEqual(
            employee.with_context(
                assume_project_timesheet_holidays_installed=False,
            )._get_timesheet_cost(as_of_day),
            5.43
        )
        self.assertEqual(
            employee.with_context(
                assume_project_timesheet_holidays_installed=True,
            )._get_timesheet_cost(as_of_day),
            5.43
        )

        self.ResourceCalendarLeave.create({
            'name': 'Global Leave',
            'resource_id': False,
            'calendar_id': employee.resource_calendar_id.id,
            'date_from': datetime(2020, 1, 1, 0, 0, 0, tzinfo=tz),
            'date_to': datetime(2020, 1, 1, 23, 59, 59, tzinfo=tz),
        })
        self.assertEqual(
            employee.with_context(
                assume_project_timesheet_holidays_installed=False,
            )._get_timesheet_cost(as_of_day),
            5.68
        )
        self.assertEqual(
            employee.with_context(
                assume_project_timesheet_holidays_installed=True,
            )._get_timesheet_cost(as_of_day),
            5.68
        )

        self.ResourceCalendarLeave.create({
            'name': 'Employee Leave',
            'resource_id': employee.resource_id.id,
            'calendar_id': employee.resource_calendar_id.id,
            'date_from': datetime(2020, 1, 2, 0, 0, 0, tzinfo=tz),
            'date_to': datetime(2020, 1, 2, 23, 59, 59, tzinfo=tz),
        })
        self.assertEqual(
            employee.with_context(
                assume_project_timesheet_holidays_installed=False,
            )._get_timesheet_cost(as_of_day),
            5.95
        )
        self.assertEqual(
            employee.with_context(
                assume_project_timesheet_holidays_installed=True,
            )._get_timesheet_cost(as_of_day),
            5.68
        )
