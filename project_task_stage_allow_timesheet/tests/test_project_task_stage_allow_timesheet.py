# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectTaskStageAllowTimesheet(TransactionCase):
    def setUp(self):
        super(TestProjectTaskStageAllowTimesheet, self).setUp()
        self.AnalyticLine = self.env["account.analytic.line"]

        self.project_1 = self.env.ref("project.project_project_1")
        self.task_1 = self.env.ref("project.project_task_1")

        self.stage_new = self.env.ref("project.project_stage_0")

    def test_01_stage_allow_timesheet(self):
        self.task_1.stage_id = self.stage_new

        values = {
            "name": "test",
            "project_id": self.project_1.id,
            "task_id": self.task_1.id,
        }
        self.AnalyticLine.create(values)

        self.stage_new.allow_timesheet = False
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.AnalyticLine.create(values)
