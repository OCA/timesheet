# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from openerp.tests.common import TransactionCase
from openerp.fields import DATE_LENGTH


class BaseCase(TransactionCase):
    def setUp(self):
        super(BaseCase, self).setUp()
        m_data = self.registry("ir.model.data")
        self.company_id = m_data.get_object_reference(
            self.cr, self.uid, "base", "main_company")[1]
        self.company = self.env['res.company'].browse(self.company_id)
        m_account = self.env['account.analytic.account']
        m_partner = self.env['res.partner']
        self.analytic_account = m_account.create({
            'name': 'Cuenta prueba', 'type': 'normal', 'use_timesheets': True})
        self.partner = m_partner.create({
            'name': 'Partner prueba'})
        self.analytic_account2 = m_account.create({
            'name': 'Cuenta prueba 2', 'type': 'normal',
            'use_timesheets': True})
        self.partner2 = m_partner.create({
            'name': 'Partner prueba 2'})

    def phonecall_create(self, vals):
        self.original = self.env["crm.phonecall"].create(vals)
        return self.original

    def check_phonecall_timesheet_asserts(self, phonecall, timesheet):
        self.assertEqual(phonecall.date[:DATE_LENGTH], timesheet.date)
        self.assertEqual(phonecall.user_id, timesheet.user_id)
        self.assertEqual(phonecall.name, timesheet.name)
        self.assertEqual(phonecall.analytic_account_id, timesheet.account_id)
        self.assertAlmostEqual(phonecall.duration / 60.0,
                               timesheet.unit_amount, places=1)
