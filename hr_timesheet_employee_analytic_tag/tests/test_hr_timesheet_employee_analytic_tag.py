# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users


class TestHrTimesheetEmployeeAnalyticTag(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag_1 = cls.env["account.analytic.tag"].create({"name": "Test tag 1"})
        cls.tag_2 = cls.env["account.analytic.tag"].create({"name": "Test tag 2"})
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "allow_timesheets": True}
        )
        cls.task = cls.env["project.task"].create(
            {"name": "Test task", "project_id": cls.project.id}
        )
        cls.user = new_test_user(
            cls.env, login="test-user", groups="hr_timesheet.group_hr_timesheet_user"
        )
        cls.employee_1 = cls.env["hr.employee"].create(
            {
                "name": "Test employee 1",
                "timesheet_analytic_tag_ids": [(6, 0, cls.tag_1.ids)],
                "user_id": cls.user.id,
            }
        )
        cls.employee_2 = cls.env["hr.employee"].create(
            {
                "name": "Test employee 2",
            }
        )
        cls.account_analytic_line_model = cls.env["account.analytic.line"]

    def _create_account_analytic_line(self, employee, tag):
        vals = {
            "name": "TEST",
            "employee_id": employee.id,
            "project_id": self.project.id,
            "task_id": self.task.id,
            "amount": 10,
        }
        if tag:
            vals["tag_ids"] = [(6, 0, tag.ids)]
        return self.account_analytic_line_model.create(vals)

    def _create_timesheet_item(self):
        view_id = "hr_timesheet.hr_timesheet_line_tree"
        timesheet = Form(self.env["account.analytic.line"], view=view_id)
        timesheet.project_id = self.project
        timesheet.task_id = self.task
        timesheet.name = "TEST"
        timesheet.unit_amount = 0.5
        return timesheet.save()

    def test_account_analytic_line_create_01(self):
        item = self._create_account_analytic_line(self.employee_1, False)
        self.assertIn(self.tag_1, item.tag_ids)
        self.assertNotIn(self.tag_2, item.tag_ids)
        item = self._create_account_analytic_line(self.employee_2, False)
        self.assertNotIn(self.tag_1, item.tag_ids)
        self.assertNotIn(self.tag_2, item.tag_ids)

    def test_account_analytic_line_create_02(self):
        item = self._create_account_analytic_line(self.employee_1, self.tag_2)
        self.assertIn(self.tag_1, item.tag_ids)
        self.assertIn(self.tag_2, item.tag_ids)
        item = self._create_account_analytic_line(self.employee_2, self.tag_2)
        self.assertNotIn(self.tag_1, item.tag_ids)
        self.assertIn(self.tag_2, item.tag_ids)

    @users("test-user")
    def test_account_analytic_line_create_03(self):
        item = self._create_timesheet_item().sudo()
        self.assertIn(self.tag_1, item.tag_ids)
        self.assertNotIn(self.tag_2, item.tag_ids)
