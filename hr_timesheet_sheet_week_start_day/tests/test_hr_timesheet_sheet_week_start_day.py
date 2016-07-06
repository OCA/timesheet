# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests import common
from openerp import fields


class TestHrTimesheetSheetWeekStartDay(common.TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheetWeekStartDay, self).setUp()
        self.hrtss_model = self.env['hr_timesheet_sheet.sheet']
        self.company = self.env.ref('base.main_company')
        self.employee = self.env.ref('hr.employee_fp')
        self.company.timesheet_range = 'week'
        self.company.timesheet_week_start = '6'

    def test_create_timesheet(self):
        hrtss = self.hrtss_model.create({'employee_id': self.employee.id,
                                         'company_id': self.company.id})
        date_from = fields.Date.from_string(hrtss.date_from)
        date_to = fields.Date.from_string(hrtss.date_to)
        weekday_from = date_from.weekday()
        weekday_to = date_to.weekday()

        self.assertEqual(weekday_from, 6, "The timesheet should start on "
                                          "Sunday")

        self.assertEqual(weekday_to, 5, "The timesheet should end on Saturday")
