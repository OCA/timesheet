# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestTimeTypeCost(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Cost Employee", "hourly_cost": 75.0}
        )
        cls.project = cls.env["project.project"].create(
            {"name": "Cost Project", "allow_timesheets": True}
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

    def _create_line(self, time_type=False, unit_amount=2.0):
        return self.env["account.analytic.line"].create(
            {
                "name": "Timesheet",
                "employee_id": self.employee.id,
                "project_id": self.project.id,
                "unit_amount": unit_amount,
                "time_type_id": time_type.id if time_type else False,
            }
        )

    def test_cost_types(self):
        self.assertEqual(self._create_line(self.type_employee).amount, -150.0)
        self.assertEqual(self._create_line().amount, -150.0)
        self.assertEqual(self._create_line(self.type_ratio).amount, -225.0)
        self.assertEqual(self._create_line(self.type_fixed).amount, -62.0)

    def test_fixed_rate_survives_an_hours_edit(self):
        line = self._create_line(self.type_fixed)
        line.unit_amount = 3.0
        self.assertEqual(line.amount, -93.0)

    def test_time_type_changes_reprice(self):
        line = self._create_line(self.type_employee)
        line.time_type_id = self.type_ratio
        self.assertEqual(line.amount, -225.0)
        line.time_type_id = False
        self.assertEqual(line.amount, -150.0)
        self.assertFalse(line.time_type_cost_type)

    def test_rate_change_does_not_reprice_existing_lines(self):
        line = self._create_line(self.type_fixed)
        self.type_fixed.fixed_cost = 40.0
        self.assertEqual(line.amount, -62.0)
        self.assertEqual(self._create_line(self.type_fixed).amount, -80.0)

    def test_constraints(self):
        with self.assertRaises(ValidationError):
            self.env["project.time.type"].create(
                {"name": "Zero Ratio", "cost_type": "ratio", "cost_ratio": 0.0}
            )
        with self.assertRaises(ValidationError):
            self.env["project.time.type"].create(
                {"name": "Negative Ratio", "cost_type": "ratio", "cost_ratio": -1.0}
            )
        for value in (0.0, -10.0):
            with self.assertRaises(ValidationError):
                self.env["project.time.type"].create(
                    {
                        "name": "Bad Fixed Cost",
                        "cost_type": "fixed",
                        "fixed_cost": value,
                    }
                )
        with self.assertRaises(ValidationError):
            self.env["project.time.type"].create(
                {
                    "name": "Shared Fixed",
                    "company_id": False,
                    "cost_type": "fixed",
                    "fixed_cost": 31.0,
                }
            )

    def test_shared_type_can_use_a_ratio(self):
        shared_type = self.env["project.time.type"].create(
            {
                "name": "Shared Overtime",
                "company_id": False,
                "cost_type": "ratio",
                "cost_ratio": 1.5,
            }
        )
        line = self._create_line(shared_type)
        self.assertEqual(line.amount, -225.0)
        self.assertEqual(line.time_type_cost_type, "ratio")
