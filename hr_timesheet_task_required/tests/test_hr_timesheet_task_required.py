# Copyright 2018 ACSONE SA/NV
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestHrTimesheetTaskRequired(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.AnalyticLine = cls.env["account.analytic.line"]
        cls.Project = cls.env["project.project"]
        cls.ProjectTask = cls.env["project.task"]

        cls.project_1 = cls.Project.create(
            {"name": "Project 1", "is_timesheet_task_required": True}
        )
        cls.project_2 = cls.Project.create({"name": "Project 2"})
        cls.task_1_p1 = cls.ProjectTask.create(
            {"name": "Task 1-1", "project_id": cls.project_1.id}
        )
        cls.task_1_p2 = cls.ProjectTask.create(
            {"name": "Task 2-1", "project_id": cls.project_2.id}
        )

    def test_timesheet_line_task_required(self):
        with self.assertRaises(ValidationError):
            self.AnalyticLine.create(
                {"name": "test", "project_id": self.project_1.id, "unit_amount": 10}
            )

        self.AnalyticLine.create(
            {
                "name": "test",
                "project_id": self.project_1.id,
                "task_id": self.task_1_p1.id,
                "unit_amount": 10,
            }
        )

    def test_timesheet_line_task_not_required(self):
        self.AnalyticLine.create(
            {"name": "test", "project_id": self.project_2.id, "unit_amount": 10}
        )

        self.AnalyticLine.create(
            {
                "name": "test",
                "project_id": self.project_2.id,
                "task_id": self.task_1_p2.id,
                "unit_amount": 10,
            }
        )
