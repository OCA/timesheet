# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestProjectTaskStageAllowTimesheet(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProjectTaskStageAllowTimesheet, cls).setUpClass()
        cls.AnalyticLine = cls.env['account.analytic.line']

        cls.project_1 = cls.env.ref('project.project_project_1')
        cls.task_1 = cls.env.ref('project.project_task_1')

        cls.stage_new = cls.env.ref('project.project_stage_data_0')

    def test_01_stage_allow_timesheet(self):
        self.stage_new.allow_timesheet = False
        self.task_1.stage_id = self.stage_new

        values = {
            'name': "test",
            'project_id': self.project_1.id,
            'task_id': self.task_1.id,
        }

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.AnalyticLine.create(values)

        self.stage_new.allow_timesheet = True
        self.AnalyticLine.create(values)
