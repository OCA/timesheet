# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetTaskStage(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project = cls.env["project.project"].create({"name": "Test project"})
        cls.analytic_account = cls.project.account_id
        cls.task = cls.env["project.task"].create(
            {"name": "Test task", "project_id": cls.project.id}
        )
        task_type_obj = cls.env["project.task.type"]
        cls.stage_open = task_type_obj.create(
            {"name": "New", "fold": False, "project_ids": [(6, 0, cls.project.ids)]}
        )
        cls.stage_close = task_type_obj.create(
            {"name": "Done", "fold": True, "project_ids": [(6, 0, cls.project.ids)]}
        )
        cls.test_user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "testuser@example.com",
            }
        )
        # Create an employee for the user
        cls.test_employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": cls.test_user.id,
            }
        )
        # Create the analytic line with a linked task and employee
        cls.line = cls.env["account.analytic.line"].create(
            {
                "name": "Test line",
                "task_id": cls.task.id,
                "account_id": cls.analytic_account.id,
                "employee_id": cls.test_employee.id,
            }
        )

    def test_open_close_task(self):
        self.line.action_close_task()
        self.assertEqual(self.line.task_id.stage_id, self.stage_close)
        self.line.action_open_task()
        self.assertEqual(self.line.task_id.stage_id, self.stage_open)

    def test_toggle_task_stage(self):
        self.line.action_toggle_task_stage()
        self.assertTrue(self.line.task_id.stage_id.fold)
        self.assertTrue(self.line.is_task_closed)
        self.line.action_toggle_task_stage()
        self.assertFalse(self.line.task_id.stage_id.fold)
        self.assertFalse(self.line.is_task_closed)
