# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProjectTaskStageAllowTimesheet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectTaskStageAllowTimesheet, cls).setUpClass()
        cls.AnalyticLine = cls.env["account.analytic.line"]

        cls.employee_1 = cls.env.ref("hr.employee_qdp")
        cls.project_1 = cls.env.ref("project.project_project_1")
        cls.task_1 = cls.env.ref("project.project_1_task_1")

        cls.stage_new = cls.env.ref("project.project_stage_0")

    def test_01_stage_allow_timesheet(self):
        self.task_1.stage_id = self.stage_new

        values = {
            "name": "test",
            "project_id": self.project_1.id,
            "task_id": self.task_1.id,
            "employee_id": self.employee_1.id,
        }
        self.AnalyticLine.create(values)

        self.stage_new.allow_timesheet = False
        with self.assertRaises(ValidationError) as e, self.env.cr.savepoint():
            self.AnalyticLine.create(values)

        self.assertIn(
            "You can't link a timesheet line to a task if its stage doesn't allow it.",
            e.exception.args[0],
        )
