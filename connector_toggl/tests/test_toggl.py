# -*- coding: utf-8 -*-

import os
import json
from openerp.tests.common import TransactionCase

class TogglTestCase(TransactionCase):
    """Tests for Bysoft connector"""

    def setUp(self):
        super(TogglTestCase, self).setUp()
        self.backend = self.env['toggl.backend']
        self.toggl_timesheet_line = self.env['toggl.hr.analytic.timesheet']
        self.hr_analytic_timesheet = self.env['hr.analytic.timesheet']
        self.users = self.env['res.users']
        self.employees = self.env['hr.employee']
        self.analytic_account = self.env['account.analytic.account']

    def test_10_all_functionality(self):

        def get_account_lines(self, account_id):
            return self.hr_analytic_timesheet.search(
                [('account_id', '=', account_id)]
            )

        # Create users
        parent = self.env.ref('product.product_category_all')
        user_dan = self.users.with_context(no_reset_password=True).create({
            'name': 'Kiplangat Dan',
            'signature': 'SignDan',
            'email': 'dan@sunflowerweb.nl',
            'login': 'dan',
            'alias_name': 'dan',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
        employee_dan = self.employees.create({
            'name': 'Kiplangat Dan',
            'user_id': user_dan.id,
            'journal_id': self.env.ref('hr_timesheet.analytic_journal').id,
        })

        # company
        company = self.env.ref('base.main_company')

        # create backend
        backend = self.backend.create({
            'name': 'Toggl Backend',
            'version': '1.0',
            'api_key': 'dummy',
            'api_url': 'dummy',
            'workspace_id': 'dummy',
        })

        # Analytic account
        account = self.env.ref('account.analytic_seagate_p1')
        lines_before = get_account_lines(self, account.id)

        # Read toggl lines from test file
        testspath = os.path.dirname(os.path.realpath(__file__))
        testfile = os.path.join(testspath, 'testdata.json')
        backend.with_context(from_file=testfile).import_records()

        # check if the new timesheet activities were added
        lines_after = get_account_lines(self, account.id)
        lines_added = lines_after - lines_before
        self.assertEquals(len(lines_added), 2)

        # check if correct hours are recorded
        # 8.0 = 2 * 4.0, aggregated because of same client+project+description
        self.assertEqual(lines_added[0].unit_amount, 8.0)
        # 2.5 = 2.4 hours rounded
        self.assertEqual(lines_added[1].unit_amount, 2.5)

        # check if correct descriptions was recorded
        self.assertEqual(lines_added[0].name, 'Done some stuff')
        self.assertEqual(lines_added[1].name, 'Done more stuff')



