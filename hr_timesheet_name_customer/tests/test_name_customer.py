# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from .common import TestCommonNameCustomer


class TestTimesheet(TestCommonNameCustomer):
    def test_custom_name(self):
        """Test when Customer Description set or not: check name and name_customer equality"""
        Timesheet = self.env["account.analytic.line"]
        timesheet1 = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task1.id,
                "name": "my first timesheet",
            }
        )
        self.assertEqual(
            timesheet1.name,
            timesheet1.name_customer,
            "Description and Custom Description should be the same",
        )

        timesheet2 = Timesheet.with_user(self.user_employee).create(
            {
                "project_id": self.project_customer.id,
                "task_id": self.task2.id,
                "name": "my second timesheet",
                "name_customer": "my second timesheet with another description",
            }
        )
        self.assertNotEqual(
            timesheet2.name,
            timesheet2.name_customer,
            "Description and Custom Description should be different",
        )
