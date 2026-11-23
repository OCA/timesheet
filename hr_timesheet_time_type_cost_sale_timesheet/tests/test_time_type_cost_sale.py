# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestTimeTypeCostSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Sale Cost Employee", "hourly_cost": 75.0}
        )
        cls.other_employee = cls.env["hr.employee"].create(
            {"name": "Other Cost Employee", "hourly_cost": 50.0}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Timesheet Service",
                "type": "service",
                "service_type": "timesheet",
                "invoice_policy": "delivery",
                "list_price": 100.0,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Cost Customer"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "price_unit": 100.0})
                ],
            }
        )
        cls.sale_order.action_confirm()
        cls.sale_line = cls.sale_order.order_line
        cls.project = cls.env["project.project"].create(
            {
                "name": "Employee Rate Project",
                "allow_billable": True,
                "allow_timesheets": True,
                "sale_line_employee_ids": [
                    Command.create(
                        {
                            "employee_id": cls.employee.id,
                            "sale_line_id": cls.sale_line.id,
                        }
                    )
                ],
            }
        )
        # A mapped cost that differs from the employee cost, so that the two
        # possible bases of the ratio are distinguishable.
        cls.project.sale_line_employee_ids.cost = 40.0
        cls.project_task_rate = cls.env["project.project"].create(
            {
                "name": "Task Rate Project",
                "allow_billable": True,
                "allow_timesheets": True,
            }
        )
        cls.project_fixed_rate = cls.env["project.project"].create(
            {
                "name": "Fixed Rate Project",
                "allow_billable": True,
                "allow_timesheets": True,
                "sale_line_id": cls.sale_line.id,
            }
        )
        cls.type_employee = cls.env["project.time.type"].create(
            {"name": "Normal Hours", "cost_type": "employee"}
        )
        cls.type_ratio = cls.env["project.time.type"].create(
            {"name": "Overtime", "cost_type": "ratio", "cost_ratio": 1.5}
        )
        cls.type_fixed = cls.env["project.time.type"].create(
            {"name": "Night Shift", "cost_type": "fixed", "fixed_cost": 31.0}
        )

    def _create_line(
        self, project=None, time_type=False, unit_amount=2.0, employee=None
    ):
        return self.env["account.analytic.line"].create(
            {
                "name": "Timesheet",
                "project_id": (project or self.project).id,
                "employee_id": (employee or self.employee).id,
                "unit_amount": unit_amount,
                "time_type_id": time_type.id if time_type else False,
            }
        )

    def test_ratio_applies_over_the_mapped_cost(self):
        line = self._create_line(time_type=self.type_ratio)
        # The mapped cost wins over the employee cost as the base of the ratio.
        self.assertEqual(line._hourly_cost(), 60.0)
        self.assertEqual(line.amount, -120.0)

    def test_employee_cost_keeps_the_mapped_cost(self):
        line = self._create_line(time_type=self.type_employee)
        self.assertEqual(line._hourly_cost(), 40.0)
        self.assertEqual(line.amount, -80.0)

    def test_no_time_type_keeps_the_mapped_cost(self):
        line = self._create_line()
        self.assertEqual(line._hourly_cost(), 40.0)
        self.assertEqual(line.amount, -80.0)

    def test_fixed_cost_replaces_the_mapped_cost(self):
        line = self._create_line(time_type=self.type_fixed)
        self.assertEqual(line._hourly_cost(), 31.0)
        self.assertEqual(line.amount, -62.0)
        line.unit_amount = 3.0
        self.assertEqual(line.amount, -93.0)

    def test_task_rate_project_keeps_the_employee_cost(self):
        line = self._create_line(
            project=self.project_task_rate, time_type=self.type_ratio
        )
        self.assertEqual(line._hourly_cost(), 112.5)
        self.assertEqual(line.amount, -225.0)

    def test_fixed_rate_project_keeps_the_employee_cost(self):
        line = self._create_line(
            project=self.project_fixed_rate, time_type=self.type_ratio
        )
        self.assertEqual(line._hourly_cost(), 112.5)
        self.assertEqual(line.amount, -225.0)

    def test_employee_rate_project_without_mapping_entry(self):
        """An employee outside the map falls back to the employee cost, once."""
        line = self._create_line(
            time_type=self.type_ratio, employee=self.other_employee
        )
        self.assertEqual(line._hourly_cost(), 75.0)
        self.assertEqual(line.amount, -150.0)

    def test_time_type_change_reprices_at_the_mapped_cost(self):
        line = self._create_line(time_type=self.type_employee)
        self.assertEqual(line.amount, -80.0)
        line.time_type_id = self.type_ratio
        self.assertEqual(line.amount, -120.0)
