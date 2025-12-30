# Copyright 2025 Acysos S.L. (https://www.acysos.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import Command, fields
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestPortalTimesheetInput(HttpCase):
    """Test the portal timesheet input functionality."""

    def setUp(self):
        """Set up the test environment."""
        super().setUp()
        # Create a user and employee
        self.user = self.env["res.users"].create(
            {
                "name": "Test Input User",
                "login": "test_input_user",
                "password": "test_input_user",
            }
        )
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "user_id": self.user.id,
            }
        )
        self.project = self.env["project.project"].create(
            {
                "name": "Test Project",
                "privacy_visibility": "portal",
                "partner_id": self.user.partner_id.id,
                "company_id": self.user.company_id.id,
            }
        )
        self.task = self.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": self.project.id,
            }
        )

    def test_access_grid(self):
        """Test accessing the timesheet grid."""
        # Authenticate
        self.authenticate(self.user.login, self.user.login)
        # Access the grid
        response = self.url_open("/my/timesheet/input")
        self.assertEqual(
            response.status_code, 200, "Should be able to access timesheet grid"
        )

    def test_portal_user_access(self):
        """Test access for a real portal user (no internal group)."""
        portal_group = self.env.ref("base.group_portal")
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal User",
                "login": "portal_user_test",
                "password": "portal_user_test",
                "groups_id": [Command.set([portal_group.id])],
            }
        )
        # Create employee for this portal user
        self.env["hr.employee"].create(
            {
                "name": "Portal Employee",
                "user_id": portal_user.id,
            }
        )

        self.authenticate(portal_user.login, portal_user.login)
        response = self.url_open("/my/timesheet/input")
        self.assertEqual(
            response.status_code,
            200,
            "Portal user should access timesheet grid",
        )

    def test_save_grid_input(self):
        """Test saving a timesheet input."""
        self.authenticate(self.user.login, self.user.login)

        today = fields.Date.today()
        day_str = today.strftime("%Y-%m-%d")

        # Data to save
        data = {
            "inputs": [
                {
                    "project_id": self.project.id,
                    "task_id": self.task.id,
                    "date": day_str,
                    "unit_amount": 2.5,
                }
            ],
            "week_start": (today - timedelta(days=today.weekday())).strftime(
                "%Y-%m-%d"
            ),
        }

        # Save
        # We can simulate the JSON-RPC call.

        payload = {"jsonrpc": "2.0", "method": "call", "params": data, "id": 123456789}

        response = self.opener.post(
            self.base_url() + "/my/timesheet/save_grid", json=payload
        )
        self.assertEqual(response.status_code, 200)

        # Check if record created
        line = self.env["account.analytic.line"].search(
            [
                ("project_id", "=", self.project.id),
                ("task_id", "=", self.task.id),
                ("date", "=", today),
                ("employee_id", "=", self.employee.id),
            ]
        )
        self.assertTrue(line, "Timesheet line should be created")
        self.assertEqual(line.unit_amount, 2.5, "Amount should be 2.5")

        # Update
        data["inputs"][0]["unit_amount"] = 4.0
        payload["params"] = data

        response = self.opener.post(
            self.base_url() + "/my/timesheet/save_grid", json=payload
        )
        self.assertEqual(response.status_code, 200)

        # or invalidate_cache() depending on version, invalidate_recordset
        # is safer in 16.0
        line.invalidate_recordset()
        self.assertEqual(line.unit_amount, 4.0, "Amount should be updated to 4.0")

    def test_get_project_tasks(self):
        """Test retrieving tasks for a project."""
        self.authenticate(self.user.login, self.user.login)
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"project_id": self.project.id},
            "id": 1,
        }
        response = self.opener.post(
            self.base_url() + "/my/timesheet/get_tasks", json=payload
        )
        self.assertEqual(response.status_code, 200)
        result = response.json().get("result")
        self.assertTrue(result, "Should return tasks")
        self.assertEqual(len(result), 1, "Should return 1 task")
        self.assertEqual(result[0]["id"], self.task.id)

    def test_access_grid_date(self):
        """Test accessing the grid with a specific date."""
        self.authenticate(self.user.login, self.user.login)
        # Test with valid date
        response = self.url_open("/my/timesheet/input?week_start=2023-01-01")
        self.assertEqual(response.status_code, 200)
        # Test with invalid date (should fallback to today)
        response = self.url_open("/my/timesheet/input?week_start=invalid-date")
        self.assertEqual(response.status_code, 200)

    def test_no_employee(self):
        """Test behavior when user is not linked to an employee."""
        # Create user without employee
        user_no_emp = self.env["res.users"].create(
            {
                "name": "No Employee User",
                "login": "no_emp_user",
                "password": "no_emp_user",
            }
        )
        self.authenticate(user_no_emp.login, user_no_emp.login)

        # Test grid access
        response = self.url_open("/my/timesheet/input")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"You must be linked to an employee", response.content)

        # Test save
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"inputs": [], "week_start": "2023-01-01"},
            "id": 2,
        }
        response = self.opener.post(
            self.base_url() + "/my/timesheet/save_grid", json=payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("result", {}).get("error"),
            "User not linked to employee",
        )

    def test_delete_entry(self):
        """Test deleting a timesheet entry by setting amount to 0."""
        self.authenticate(self.user.login, self.user.login)
        today = fields.Date.today()

        # Create initial entry
        line = self.env["account.analytic.line"].create(
            {
                "project_id": self.project.id,
                "task_id": self.task.id,
                "date": today,
                "unit_amount": 2.0,
                "employee_id": self.employee.id,
                "name": "/",
            }
        )

        data = {
            "inputs": [
                {
                    "project_id": self.project.id,
                    "task_id": self.task.id,
                    "date": today.strftime("%Y-%m-%d"),
                    "unit_amount": 0.0,
                }
            ],
            "week_start": today.strftime("%Y-%m-%d"),
        }
        payload = {"jsonrpc": "2.0", "method": "call", "params": data, "id": 3}

        response = self.opener.post(
            self.base_url() + "/my/timesheet/save_grid", json=payload
        )
        self.assertEqual(response.status_code, 200)

        # Verify deletion
        self.assertFalse(line.exists(), "Timesheet line should be deleted")

    def test_error_handling(self):
        """Test error handling in save_grid_inputs."""
        self.authenticate(self.user.login, self.user.login)

        # Malformed date
        data = {
            "inputs": [
                {
                    "project_id": self.project.id,
                    "date": "invalid-date",
                    "unit_amount": 2.0,
                }
            ],
            "week_start": "2023-01-01",
        }
        payload = {"jsonrpc": "2.0", "method": "call", "params": data, "id": 4}

        response = self.opener.post(
            self.base_url() + "/my/timesheet/save_grid", json=payload
        )
        self.assertEqual(response.status_code, 200)
        result = response.json().get("result")
        self.assertTrue(result.get("error"), "Should return an error")

    def test_project_only_entry(self):
        """Test creating an entry on a project without a task."""
        self.authenticate(self.user.login, self.user.login)
        today = fields.Date.today()

        data = {
            "inputs": [
                {
                    "project_id": self.project.id,
                    "task_id": False,
                    "date": today.strftime("%Y-%m-%d"),
                    "unit_amount": 3.0,
                }
            ],
            "week_start": today.strftime("%Y-%m-%d"),
        }
        payload = {"jsonrpc": "2.0", "method": "call", "params": data, "id": 5}

        response = self.opener.post(
            self.base_url() + "/my/timesheet/save_grid", json=payload
        )
        self.assertEqual(response.status_code, 200)

        line = self.env["account.analytic.line"].search(
            [
                ("project_id", "=", self.project.id),
                ("task_id", "=", False),
                ("date", "=", today),
                ("employee_id", "=", self.employee.id),
            ]
        )
        self.assertTrue(line, "Project-only timesheet line should be created")
        self.assertEqual(line.unit_amount, 3.0)

        # Access grid to verify get_key logic for project-only lines
        response = self.url_open("/my/timesheet/input")
        self.assertEqual(response.status_code, 200)
