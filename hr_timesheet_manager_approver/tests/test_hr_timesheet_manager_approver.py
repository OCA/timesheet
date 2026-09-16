# Copyright 2025 Moduon Team SL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetManagerApprover(BaseCommon):
    """Test that timesheet approvers can manage subordinate timesheets."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager_user = new_test_user(
            cls.env,
            login="manager_user",
            groups="hr_timesheet.group_hr_timesheet_approver,project.group_project_user",
        )
        cls.subordinate_user = new_test_user(
            cls.env,
            login="subordinate_user",
            groups="hr_timesheet.group_hr_timesheet_user,project.group_project_user",
        )
        cls.other_user = new_test_user(
            cls.env,
            login="other_user",
            groups="hr_timesheet.group_hr_timesheet_user,project.group_project_user",
        )
        cls.manager_employee = cls.env["hr.employee"].create(
            {
                "name": "Manager Employee",
                "user_id": cls.manager_user.id,
            }
        )
        cls.subordinate_employee = cls.env["hr.employee"].create(
            {
                "name": "Subordinate Employee",
                "user_id": cls.subordinate_user.id,
                "parent_id": cls.manager_employee.id,
            }
        )
        cls.other_manager_user = new_test_user(
            cls.env,
            login="other_manager_user",
            groups="hr_timesheet.group_hr_timesheet_approver,project.group_project_user",
        )
        cls.other_manager_employee = cls.env["hr.employee"].create(
            {
                "name": "Other Manager Employee",
                "user_id": cls.other_manager_user.id,
            }
        )
        cls.other_employee = cls.env["hr.employee"].create(
            {
                "name": "Other Employee",
                "user_id": cls.other_user.id,
                "parent_id": cls.other_manager_employee.id,
            }
        )
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "AA Test", "plan_id": cls.analytic_plan.id}
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
                "privacy_visibility": "followers",
                "account_id": cls.analytic_account.id,
            }
        )
        cls.manager_env = cls.env(user=cls.manager_user)

    def test_manager_can_read_subordinate_timesheet(self):
        """Manager with approver group can read subordinate timesheet."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.subordinate_employee.id,
                "unit_amount": 1,
            }
        )
        record = self.manager_env["account.analytic.line"].browse(timesheet.id)
        self.assertTrue(record.exists())
        self.assertEqual(record.name, "Test Timesheet")

    def test_manager_can_write_subordinate_timesheet(self):
        """Manager with approver group can write subordinate timesheet."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.subordinate_employee.id,
                "unit_amount": 1,
            }
        )
        record = self.manager_env["account.analytic.line"].browse(timesheet.id)
        record.write({"name": "Updated Timesheet"})
        self.assertEqual(record.name, "Updated Timesheet")

    def test_manager_can_create_timesheet_for_subordinate(self):
        """Manager with approver group can create timesheet for subordinate."""
        record = self.manager_env["account.analytic.line"].create(
            {
                "name": "Manager Created Timesheet",
                "project_id": self.project.id,
                "employee_id": self.subordinate_employee.id,
                "unit_amount": 2,
            }
        )
        self.assertTrue(record.exists())

    def test_manager_can_unlink_subordinate_timesheet(self):
        """Manager with approver group can delete subordinate timesheet."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Test Timesheet",
                "project_id": self.project.id,
                "employee_id": self.subordinate_employee.id,
                "unit_amount": 1,
            }
        )
        record = self.manager_env["account.analytic.line"].browse(timesheet.id)
        record.unlink()
        self.assertFalse(
            self.env["account.analytic.line"].browse(timesheet.id).exists()
        )

    def test_manager_cannot_access_non_subordinate_timesheet(self):
        """Manager with approver group cannot access timesheet of non-subordinate."""
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "Other Timesheet",
                "project_id": self.project.id,
                "employee_id": self.other_employee.id,
                "unit_amount": 1,
            }
        )
        found = self.manager_env["account.analytic.line"].search(
            [("id", "=", timesheet.id)]
        )
        self.assertFalse(found, "Manager should not see non-subordinate timesheet")
