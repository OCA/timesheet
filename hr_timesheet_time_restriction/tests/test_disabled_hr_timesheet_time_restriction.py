# Copyright 2022 Dinar Gabbasov
# Copyright 2022 Ooops404
# Copyright 2022 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHrTimesheetTimeRestriction(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.project = self.env["project.project"].create({"name": "Test project"})
        self.analytic_account = self.project.analytic_account_id
        self.task = self.env["project.task"].create(
            {
                "name": "Test task",
                "project_id": self.project.id,
            }
        )
        self.config = self.env["res.config.settings"].create({})
        self.config.use_timesheet_restriction = False
        self.config.execute()

    def test_project_restriction_days(self):
        self.project.timesheet_restriction_days = 1
        # check that we can create new timesheet
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today(),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")
        # check that we can create new timesheet with date before
        # that current date - 1
        line = False
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today() - datetime.timedelta(days=2),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")

    def test_project_restriction_days_by_config(self):
        config = self.env["res.config.settings"].create({})
        config.timesheet_restriction_days = 1
        config.execute()
        # check that we can create new timesheet
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today() - datetime.timedelta(days=1),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")
        # check that we cannot create new timesheet with date before
        # that current date - 1
        line = False
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today() - datetime.timedelta(days=2),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")

    def test_project_restriction_days_ignore_config(self):
        config = self.env["res.config.settings"].create({})
        config.timesheet_restriction_days = 1
        config.execute()
        self.project.timesheet_restriction_days = 2
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today() - datetime.timedelta(days=2),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")
        # check that we cannot create new timesheet with date before
        # that current date - 2
        line = False
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today() - datetime.timedelta(days=3),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")

    def test_project_restriction_days_ignore_for_timesheet_time_manager(self):
        group = self.ref("hr_timesheet_time_restriction.group_timesheet_time_manager")
        self.env.user.groups_id = [(4, group)]
        self.project.timesheet_restriction_days = 1
        # check that we can create new timesheet with date before
        # that current date - 1
        line = self.env["account.analytic.line"].create(
            {
                "date": datetime.date.today() - datetime.timedelta(days=2),
                "task_id": self.task.id,
                "project_id": self.project.id,
                "account_id": self.analytic_account.id,
                "name": "Test line",
            }
        )
        self.assertTrue(line, "Timesheet should be created")

    def test_set_negative_project_restriction_days(self):
        try:
            self.project.timesheet_restriction_days = -1
        except ValidationError:
            self.project.timesheet_restriction_days = 0
        self.assertNotEqual(self.project.timesheet_restriction_days, 0)

    def test_set_negative_config_restriction_days(self):
        config = self.env["res.config.settings"].create({})
        config.timesheet_restriction_days = -1
        config._onchange_timesheet_restriction_days()
        config.execute()
        self.assertEqual(config.timesheet_restriction_days, 0)
