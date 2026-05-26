# © 202& Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProjectTaskTimeoff(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Internal Project",
            }
        )

        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Time Off Task 1",
                "project_id": cls.project.id,
            }
        )

        cls.task_disabled = cls.env["project.task"].create(
            {
                "name": "Task Disabled",
                "project_id": cls.project.id,
                "timeoff_enable_use_timesheets": False,
            }
        )

        cls.env.company.leave_timesheet_task_id = cls.task.id
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Test Leaves",
                "requires_allocation": "no",
                "timesheet_project_id": cls.project.id,
                "timesheet_task_id": cls.task_disabled.id,
            }
        )

    def test_timeoff_enable_use_timesheets_behavior(self):
        self.task.is_timeoff_task = True
        self.assertTrue(self.task.is_timeoff_task)

        self.task.timeoff_enable_use_timesheets = True

        self.task.invalidate_recordset(["is_timeoff_task"])
        self.assertFalse(self.task.is_timeoff_task)

    def test_search_is_timeoff_task_filtering(self):
        self.task.timeoff_enable_use_timesheets = True

        self.leave_type.flush_recordset(["timesheet_project_id", "timesheet_task_id"])
        self.env.invalidate_all()

        result_true = self.task._search_is_timeoff_task("=", True)
        ids_true = result_true[0][2]
        self.assertIn(self.task.id, ids_true)
        self.assertNotIn(self.task_disabled.id, ids_true)

        result_false = self.task._search_is_timeoff_task("=", False)
        ids_false = result_false[0][2]
        self.assertNotIn(self.task.id, ids_false)
        self.assertIn(self.task_disabled.id, ids_false)
