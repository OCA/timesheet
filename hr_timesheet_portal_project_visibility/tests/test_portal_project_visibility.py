# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import Command
from odoo.osv import expression
from odoo.tests import HttpCase, tagged

from odoo.addons.project.tests.test_project_sharing import TestProjectSharingCommon


@tagged("post_install", "-at_install")
class TestPortalProjectVisibility(TestProjectSharingCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.AnalyticLine = cls.env["account.analytic.line"]
        # Instances
        cls.user_portal.password = "chell"
        cls.project_portal.write(
            {
                "allow_timesheets": True,
                "collaborator_ids": [
                    Command.create({"partner_id": cls.user_portal.partner_id.id})
                ],
            }
        )
        cls.project_portal.message_subscribe(partner_ids=cls.user_portal.partner_id.ids)
        cls.task_portal.allocated_hours = 10
        cls.employee = cls.env["hr.employee"].create({"name": "Timesheet Employee"})
        cls.timesheet = cls._create_timesheet("Portal visible timesheet", cls.employee)

    @classmethod
    def _create_timesheet(cls, name, employee, **kwargs):
        return cls.AnalyticLine.create(
            {
                "name": name,
                "project_id": cls.project_portal.id,
                "task_id": cls.task_portal.id,
                "employee_id": employee.id,
                "unit_amount": 2,
                **kwargs,
            }
        )

    def _portal_timesheets(self):
        domain = self.AnalyticLine.with_user(
            self.user_portal
        )._timesheet_get_portal_domain()
        return self.AnalyticLine.sudo().search(
            expression.AND([domain, [("project_id", "=", self.project_portal.id)]])
        )

    def _portal_readable_timesheets(self):
        return self.AnalyticLine.with_user(self.user_portal).search(
            [("project_id", "=", self.project_portal.id)]
        )

    def test_portal_domain(self):
        self.assertEqual(self._portal_timesheets(), self.timesheet)
        self.project_portal.show_timesheets_in_portal = False
        self.assertFalse(self._portal_timesheets())

    def test_portal_access(self):
        self.assertEqual(self._portal_readable_timesheets(), self.timesheet)
        self.project_portal.show_timesheets_in_portal = False
        self.assertFalse(self._portal_readable_timesheets())

    def test_internal_access(self):
        self.user_projectuser.groups_id += self.env.ref(
            "hr_timesheet.group_hr_timesheet_approver"
        )
        self.project_portal.show_timesheets_in_portal = False
        timesheets = self.AnalyticLine.with_user(self.user_projectuser).search(
            [("project_id", "=", self.project_portal.id)]
        )
        self.assertEqual(timesheets, self.timesheet)

    def test_own_timesheets(self):
        employee = self.env["hr.employee"].create(
            {"name": "Portal Employee", "user_id": self.user_portal.id}
        )
        own_timesheet = self._create_timesheet(
            "Own timesheet", employee, user_id=self.user_portal.id
        )
        self.project_portal.show_timesheets_in_portal = False
        self.assertEqual(self._portal_timesheets(), own_timesheet)
        self.assertEqual(self._portal_readable_timesheets(), own_timesheet)

    def test_task_portal_page(self):
        self.authenticate("chell", "chell")
        url = f"/my/tasks/{self.task_portal.id}"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("task_timesheets", response.text)
        self.assertIn("Allocated Time", response.text)
        self.project_portal.show_timesheets_in_portal = False
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.task_portal.name, response.text)
        self.assertNotIn("task_timesheets", response.text)
        self.assertNotIn("Allocated Time", response.text)

    def test_portal_timesheets_page(self):
        self.authenticate("chell", "chell")
        response = self.url_open("/my/timesheets")
        self.assertIn(self.timesheet.name, response.text)
        self.project_portal.show_timesheets_in_portal = False
        response = self.url_open("/my/timesheets")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.timesheet.name, response.text)
