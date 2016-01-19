# -*- coding: utf-8 -*-
# © 2016 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class CrmPhonecallCase(TransactionCase):
    def test_timesheet_prepare(self):
        analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test account', 'type': 'normal', 'use_timesheets': True})
        partner = self.env['res.partner'].create({
            'name': 'Test partner'})
        vals = {
            'date': '2015-08-21 10:15:00',
            'duration': 15,
            'name': 'test_01',
            'analytic_account_id': analytic_account.id,
            'partner_id': partner.id,
            'user_id': self.uid
        }
        phonecall = self.env["crm.phonecall"].create(vals)
        self.assertEqual(phonecall.partner_id.id,
                         phonecall.timesheet_ids[0].other_partner_id.id)
