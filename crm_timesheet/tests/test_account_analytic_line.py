# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase


class AccountAnalyticLineCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(AccountAnalyticLineCase, cls).setUpClass()
        Account = cls.env["account.analytic.account"]
        Project = cls.env["project.project"]
        cls.Line = cls.env["account.analytic.line"]
        cls.account1 = Account.create({
            "name": "Account 1",
        })
        cls.account2 = Account.create({
            "name": "Account 2",
        })
        cls.project0 = Project.create({
            "name": "Project 0",
        })
        cls.project11 = Project.create({
            "name": "Project 1.1",
            "analytic_account_id": cls.account1.id,
        })
        cls.project12 = Project.create({
            "name": "Project 1.2",
            "analytic_account_id": cls.account1.id,
        })
        cls.project21 = Project.create({
            "name": "Project 2.1",
            "analytic_account_id": cls.account2.id,
        })

    def test_onchange_account_multi_project(self):
        """Changing the account leaves empty project."""
        line = self.Line.new({
            "account_id": self.account1,
        })
        line._onchange_account_id()
        self.assertFalse(line.project_id)

    def test_onchange_account_single_project(self):
        """Changing account sets project."""
        line = self.Line.new({
            "account_id": self.account2,
        })
        line._onchange_account_id()
        self.assertEqual(line.project_id, self.project21)

    def test_onchange_account_wrong_project(self):
        """Changing account unsets project."""
        line = self.Line.new({
            "project_id": self.project21,
        })
        line._onchange_project_id()
        self.assertEqual(line.account_id, self.account2)
        line.account_id = self.account1
        line._onchange_account_id()
        self.assertFalse(line.project_id)

    def test_onchange_project(self):
        """Changing the project changes the account."""
        line = self.Line.new({
            "project_id": self.project21,
        })
        line._onchange_project_id()
        self.assertEqual(line.account_id, self.account2)
        line.project_id = self.project11
        line._onchange_project_id()
        self.assertEqual(line.account_id, self.account1)
        line.project_id = self.project0
        line._onchange_project_id()
        self.assertFalse(line.account_id)
