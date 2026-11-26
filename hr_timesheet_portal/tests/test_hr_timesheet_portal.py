# Copyright 2026 Innovara Ltd - Manuel Fombuena
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestHrTimesheetPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = new_test_user(
            cls.env,
            login="hr_timesheet_portal_user",
            groups="base.group_portal,hr_timesheet_portal.group_hr_timesheet_portal",
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Portal Employee", "user_id": cls.portal_user.id}
        )
        Project = cls.env["project.project"]
        Task = cls.env["project.task"]
        cls.project = Project.create(
            {
                "name": "Portal Project",
                "privacy_visibility": "portal",
                "allow_timesheets": True,
            }
        )
        cls.task = Task.create({"name": "Portal Task", "project_id": cls.project.id})
        cls.task.message_subscribe(partner_ids=cls.portal_user.partner_id.ids)
        # Portal-visible too, but not followed by the portal user
        cls.other_project = Project.create(
            {
                "name": "Other Project",
                "privacy_visibility": "portal",
                "allow_timesheets": True,
            }
        )
        cls.other_task = Task.create(
            {"name": "Other Task", "project_id": cls.other_project.id}
        )

    def _line_values(self, task, **values):
        return {
            "name": "/",
            "project_id": task.project_id.id,
            "task_id": task.id,
            "account_id": task.project_id.account_id.id,
            "user_id": self.portal_user.id,
            "unit_amount": 0,
            **values,
        }

    def test_portal_user_manages_lines_on_followed_task(self):
        lines = self.env["account.analytic.line"].with_user(self.portal_user)
        line = lines.create(self._line_values(self.task))
        line.write({"name": "Portal line", "unit_amount": 2})
        self.assertEqual(line.sudo().name, "Portal line")
        self.assertEqual(line.sudo().unit_amount, 2)
        line.unlink()
        self.assertFalse(line.sudo().exists())

    def test_portal_user_cannot_create_lines_on_other_task(self):
        lines = self.env["account.analytic.line"].with_user(self.portal_user)
        with self.assertRaises(AccessError):
            lines.create(self._line_values(self.other_task))

    def test_portal_user_cannot_edit_lines_on_other_task(self):
        line = self.env["account.analytic.line"].create(
            self._line_values(self.other_task, employee_id=self.employee.id)
        )
        with self.assertRaises(AccessError):
            line.with_user(self.portal_user).write({"unit_amount": 3})
        with self.assertRaises(AccessError):
            line.with_user(self.portal_user).unlink()

    def test_portal_tour(self):
        self.start_tour(
            f"/my/tasks/{self.task.id}",
            "hr_timesheet_portal_tour",
            login=self.portal_user.login,
        )
        self.assertFalse(
            self.env["account.analytic.line"].search(
                [("task_id", "=", self.task.id), ("name", "=", "Portal tour line")]
            )
        )
