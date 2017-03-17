# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
#     (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo import fields


class TestHrTimesheetSheetWeekStartDay(common.TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheetWeekStartDay, self).setUp()
        self.hrtss_model = self.env['hr_timesheet_sheet.sheet']
        self.company = self.env.ref('base.main_company')
        self.company.timesheet_range = 'week'
        self.company.timesheet_week_start = '6'

        # Create an employee:
        user_id = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'user',
            'email': 'test.user@example.com',
        }).id
        resource_id = self.env['resource.resource'].create({
            'name': 'Test resource',
            'resource_type': 'user',
            'user_id': user_id
        }).id
        self.employee = self.env['hr.employee'].create({
            'resource_id': resource_id
        })

    def test_create_timesheet(self):
        """Tests the the start and end day of the week in employee
        timesheet."""
        hrtss = self.hrtss_model.create({'employee_id': self.employee.id,
                                         'company_id': self.company.id})
        date_from = fields.Date.from_string(hrtss.date_from)
        date_to = fields.Date.from_string(hrtss.date_to)
        weekday_from = date_from.weekday()
        weekday_to = date_to.weekday()

        self.assertEqual(weekday_from, 6, "The timesheet should start on "
                                          "Sunday")

        self.assertEqual(weekday_to, 5, "The timesheet should end on Saturday")
