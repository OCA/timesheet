# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestHrTimesheetTaskRequired(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrTimesheetTaskRequired, cls).setUpClass()
        cls.AnalyticLine = cls.env['account.analytic.line']
        cls.Project = cls.env['project.project']
        cls.ProjectTask = cls.env['project.task']

        cls.project_1 = cls.Project.create({
            'name': "Project 1"
        })
        cls.task_1_p1 = cls.ProjectTask.create({
            'name': "Task 1",
            'project_id': cls.project_1.id,
        })

    def test_timesheet_line_task_required(self):
        with self.assertRaises(ValidationError):
            self.AnalyticLine.create({
                'name': "test",
                'project_id': self.project_1.id,
                'unit_amount': 10,
            })

        line = self.AnalyticLine.create({
            'name': "test",
            'project_id': self.project_1.id,
            'task_id': self.task_1_p1.id,
            'unit_amount': 10,
        })
        self.assertTrue(bool(line))
