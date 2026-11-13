# Copyright (C) 2025: BizzAppDev Systems Pvt. Ltd.(https://www.bizzappdev.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase

CLOSED_STATES = {
    "1_done": "Done",
    "1_canceled": "Cancelled",
}


class TestTaskDomainStages(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Company = cls.env.user.company_id
        Project = cls.env["project.project"]
        Task = cls.env["project.task"]

        cls.project = Project.create(
            {
                "name": "Test Project",
                "allow_timesheets": True,
                "company_id": Company.id,
            }
        )

        cls.task_open = Task.create(
            {
                "name": "Open Task",
                "project_id": cls.project.id,
                "state": "01_in_progress",
                "company_id": Company.id,
            }
        )
        cls.task_done = Task.create(
            {
                "name": "Done Task",
                "project_id": cls.project.id,
                "state": "1_done",
                "company_id": Company.id,
            }
        )
        cls.task_cancelled = Task.create(
            {
                "name": "Cancelled Task",
                "project_id": cls.project.id,
                "state": "1_canceled",
                "company_id": Company.id,
            }
        )

    def test_task_id_domain(self):
        """Check that the task_id domain excludes closed and cancelled tasks."""
        domain = [
            ("project_id", "=", self.project.id),
            ("company_id", "in", [self.env.user.company_id.id, False]),
            ("project_id.allow_timesheets", "=", True),
            ("state", "not in", list(CLOSED_STATES.keys())),
        ]
        tasks = self.env["project.task"].search(domain)

        self.assertIn(self.task_open, tasks)
        self.assertNotIn(self.task_done, tasks)
        self.assertNotIn(self.task_cancelled, tasks)
