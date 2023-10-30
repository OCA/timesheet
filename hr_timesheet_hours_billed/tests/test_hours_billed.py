# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import tagged

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@tagged("-at_install", "post_install")
class TestCommonHourBilled(TestCommonSaleTimesheet):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def setUp(self):

        super().setUp()
        self.task_rate_task = self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": self.project_task_rate.id,
                "sale_line_id": self.so.order_line[0].id,
            }
        )

    def test_compute_hours_billed(self):
        # create some timesheet on this task
        timesheet1 = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "project_id": self.project_task_rate.id,
                "task_id": self.task_rate_task.id,
                "unit_amount": 5,
                "employee_id": self.employee_manager.id,
                "approved": True,
            }
        )

        # Check on creation if unit_amount_billed not set it must be equal unit_amount
        self.assertEqual(
            timesheet1.unit_amount,
            timesheet1.unit_amount_billed,
            "Hours Billed and Hours Spent should be the same",
        )
        # Create some timesheet on this task
        timesheet2 = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "project_id": self.project_task_rate.id,
                "task_id": self.task_rate_task.id,
                "unit_amount": 5,
                "unit_amount_billed": 10,
                "employee_id": self.employee_manager.id,
            }
        )
        # Check on creation if unit_amount_billed set it shouldn't be equal unit_amount
        self.assertNotEqual(
            timesheet2.unit_amount,
            timesheet2.unit_amount_billed,
            "Hours Billed and Hours Spent should be different",
        )
        # Check about recompute qty_delivered after changing unit_amount_billed
        before_change_amount_billed = self.so.order_line[0].qty_delivered
        timesheet1.write({"unit_amount_billed": 20.0})

        self.assertNotEqual(
            before_change_amount_billed,
            self.so.order_line[0].qty_delivered,
            "qty_deliverede must be recompute, after changing unit_amount_billed",
        )

        # Check about recompute qty_delivered after changing approved
        before_change_approved = self.so.order_line[0].qty_delivered
        timesheet1.write({"approved": False})

        self.assertNotEqual(
            before_change_approved,
            self.so.order_line[0].qty_delivered,
            "qty_deliverede must be recompute, after changing approved",
        )

    def test_compute_approved_user_id(self):
        # Create some timesheet on this task
        timesheet3 = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "project_id": self.project_task_rate.id,
                "task_id": self.task_rate_task.id,
                "unit_amount": 5,
                "employee_id": self.employee_manager.id,
            }
        )
        uid_before_change_approved = timesheet3.approved_user_id

        timesheet3.write({"approved": True})
        # Check about changing approved_user_id after changing state of approved to "yes"
        self.assertNotEqual(
            uid_before_change_approved,
            timesheet3.approved_user_id,
            "approved_user_id must be different",
        )

    def test_compute_approved_date(self):
        # Create some timesheet on this task
        timesheet4 = self.env["account.analytic.line"].create(
            {
                "name": "Test Line",
                "project_id": self.project_task_rate.id,
                "task_id": self.task_rate_task.id,
                "unit_amount": 5,
                "employee_id": self.employee_manager.id,
            }
        )
        # Check about changing approved_date after changing state of approved to "yes"
        date_before_change_approved = timesheet4.approved_date
        timesheet4.write({"approved": True})
        self.assertNotEqual(
            date_before_change_approved,
            timesheet4.approved_date,
            "approved_date must be different",
        )
