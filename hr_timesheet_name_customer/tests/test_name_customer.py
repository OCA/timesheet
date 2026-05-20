# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from .common import TestCommonNameCustomer


class TestTimesheet(TestCommonNameCustomer):
    def test_01_create_default(self):
        """Test unset Customer Description: check name equality"""
        Timesheet = self.env["account.analytic.line"]
        timesheet = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my first timesheet",
            }
        )
        self.assertEqual(timesheet.name_customer, "my first timesheet")

    def test_02_update_recompute(self):
        """Test if name_customer recomputes when name changes"""
        Timesheet = self.env["account.analytic.line"]
        timesheet = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "initial",
            }
        )
        timesheet.name = "updated"
        # Force recompute if necessary
        timesheet._compute_name_customer()
        self.assertEqual(timesheet.name_customer, "updated")

    def test_03_explicit_value(self):
        """Test when Customer Description is explicitly set"""
        Timesheet = self.env["account.analytic.line"]
        timesheet = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task2.id,
                "name": "technical name",
                "name_customer": "customer friendly name",
            }
        )
        self.assertEqual(timesheet.name_customer, "customer friendly name")

    def test_04_empty_name(self):
        """Test with empty name"""
        Timesheet = self.env["account.analytic.line"]
        timesheet = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": False,
            }
        )
        self.assertFalse(timesheet.name_customer)
