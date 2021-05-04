# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrTimesheetTaskDomain(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.project = self.env["project.project"].create({"name": "Test project"})
        self.analytic_account = self.project.analytic_account_id
        self.task = self.env["project.task"].create(
            {"name": "Test task", "project_id": self.project.id}
        )
        self.line = self.env["account.analytic.line"].create(
            {
                "task_id": self.task.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )

    def test_onchange_project_id(self):
        record = self.env["account.analytic.line"].new()
        record.task_id = self.task.id
        record.project_id = self.project.id
        action = record._onchange_project_id()
        self.assertTrue(action["domain"]["task_id"])
        self.assertEqual(record.task_id, self.task)
        record.project_id = False
        action = record._onchange_project_id()
        self.assertEqual(action["domain"]["task_id"], [])
