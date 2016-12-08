# -*- coding: utf-8 -*-
# © ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil.relativedelta import relativedelta

import openerp.tests.common as common


class TestChangePeriod(common.TransactionCase):

    def setUp(self):
        super(TestChangePeriod, self).setUp()
        self.htss_model = self.env['hr_timesheet_sheet.sheet']
        self.wz_model = self.env['hr.timesheet.sheet.change.period.wizard']

        self.hrat1 = self.ref('hr_timesheet_sheet_change_period.hat_1')
        self.hrat2 = self.ref('hr_timesheet_sheet_change_period.hat_2')
        self.hrat6 = self.ref('hr_timesheet_sheet_change_period.hat_6')
        self.hrat7 = self.ref('hr_timesheet_sheet_change_period.hat_7')

        self.htss = self.ref(
            'hr_timesheet_sheet_change_period.htss_4_changeperiod')

    def test_change_period(self):
        htss = self.htss_model.browse(self.htss)
        all_hrats = set([self.hrat1, self.hrat1, self.hrat6, self.hrat7, ])

        # 1. Verify demo data
        hrats = set([hrat.id for hrat in htss.timesheet_ids])
        hrats = list(all_hrats - hrats)
        self.assertEqual(hrats, [self.hrat7], "Wrong demo data")

        # 2. Create a wizard
        ctx = {'active_id': htss.id}
        wz = self.wz_model.with_context(ctx).create({})
        self.assertEqual(
            wz.sheet_id.id, htss.id,
            "Create Wizard: Wrong sheet_id value")
        self.assertEqual(
            wz.date_from, htss.date_from,
            "Create Wizard: Wrong date_from value")
        self.assertEqual(
            wz.date_to, htss.date_to,
            "Create Wizard: Wrong date_to value")

        # 3.1 Update Period - add one day to all two dates
        df = datetime.strptime(wz.date_from, '%Y-%m-%d')
        dt = datetime.strptime(wz.date_to, '%Y-%m-%d')
        vals = {
            'date_from': df+relativedelta(days=1),
            'date_to': dt+relativedelta(days=1),
        }
        wz.write(vals)
        # 3.2 Change Period
        wz.change()
        hrats = set([hrat.id for hrat in htss.timesheet_ids])
        hrats = list(all_hrats - hrats)
        self.assertEqual(
            hrats, [self.hrat1],
            "Change Period: Wrong timesheet_ids value")

        # 4.1 Revert the change
        df = datetime.strptime(wz.date_from, '%Y-%m-%d')
        dt = datetime.strptime(wz.date_to, '%Y-%m-%d')
        vals = {
            'date_from': df+relativedelta(days=-1),
            'date_to': dt+relativedelta(days=-1),
        }
        wz.write(vals)
        # 4.2 Change Period to recover the initial situation
        wz.change()
        hrats = set([hrat.id for hrat in htss.timesheet_ids])
        hrats = list(all_hrats - hrats)
        self.assertEqual(
            hrats, [self.hrat7],
            "Revert Period: Wrong timesheet_ids value")
        pass
