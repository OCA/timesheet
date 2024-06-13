# Copyright 2024 Binhex - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests import common


class TestHrTimesheetTimeTypeCostRule(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrTimesheetTimeTypeCostRule, cls).setUpClass()

        cls.employee = cls.env.ref("hr.employee_qdp")
        cls.old_analytic_line = cls.env.ref(
            "hr_timesheet.project_1_task_1_account_analytic_line_5"
        )
        cls.project_id = cls.env.ref("project.project_project_1")
        cls.task_id = cls.env.ref("project.project_1_task_8")
        cls.project_type_no_rule = cls.env["project.time.type"].create(
            {
                "name": "No Rule",
                "apply_cost_rules": False,
            }
        )
        cls.project_type_fixed_rule = cls.env["project.time.type"].create(
            {
                "name": "Fixed Rule",
                "apply_cost_rules": True,
                "cost_rule_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "cost_rule_type": "fixed",
                            "fixed_cost": -10,
                        },
                    )
                ],
            }
        )
        cls.project_type_ratio_rule = cls.env["project.time.type"].create(
            {
                "name": "Ratio Rule",
                "apply_cost_rules": True,
                "cost_rule_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "cost_rule_type": "ratio",
                            "ratio_value": 1.5,
                        },
                    )
                ],
            }
        )
        cls.project_type_domain_mix_rule = cls.env["project.time.type"].create(
            {
                "name": "Mix Rule",
                "apply_cost_rules": True,
                "cost_rule_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "cost_rule_type": "fixed",
                            "fixed_cost": -10,
                            "domain": "[('id', '=', %s)]" % cls.employee.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "sequence": 2,
                            "cost_rule_type": "ratio",
                            "ratio_value": 1.5,
                            "domain": "[('id', '!=', %s)]" % cls.employee.id,
                        },
                    ),
                ],
            }
        )

    def test_01_create_analytic_line(self):
        new_analytic_line_01 = self.env["account.analytic.line"].create(
            {
                "name": "Test",
                "project_id": self.project_id.id,
                "task_id": self.task_id.id,
                "unit_amount": 2,
                "employee_id": self.employee.id,
                "time_type_id": self.project_type_no_rule.id,
            }
        )
        self.assertEqual(new_analytic_line_01.amount, -150)
        new_analytic_line_02 = self.env["account.analytic.line"].create(
            {
                "name": "Test",
                "project_id": self.project_id.id,
                "task_id": self.task_id.id,
                "unit_amount": 2,
                "employee_id": self.employee.id,
                "time_type_id": self.project_type_fixed_rule.id,
            }
        )
        self.assertEqual(
            self.project_type_fixed_rule.cost_rule_ids[0].display_value, -10
        )
        self.assertEqual(new_analytic_line_02.amount, -20)
        new_analytic_line_03 = self.env["account.analytic.line"].create(
            {
                "name": "Test",
                "project_id": self.project_id.id,
                "task_id": self.task_id.id,
                "unit_amount": 2,
                "employee_id": self.employee.id,
                "time_type_id": self.project_type_ratio_rule.id,
            }
        )
        self.assertEqual(
            self.project_type_ratio_rule.cost_rule_ids[0].display_value, 1.5
        )
        self.assertEqual(new_analytic_line_03.amount, -225)
        new_analytic_line_04 = self.env["account.analytic.line"].create(
            {
                "name": "Test",
                "project_id": self.project_id.id,
                "task_id": self.task_id.id,
                "unit_amount": 2,
                "employee_id": self.employee.id,
                "time_type_id": self.project_type_domain_mix_rule.id,
            }
        )
        self.assertEqual(new_analytic_line_04.amount, -20)

    def test_02_write_analytic_line(self):
        self.assertEqual(self.old_analytic_line.amount, -150)
        self.assertEqual(self.old_analytic_line.unit_amount, 2)
        self.assertEqual(self.old_analytic_line.employee_id, self.employee)
        self.old_analytic_line.write({"time_type_id": self.project_type_no_rule.id})
        self.assertEqual(self.old_analytic_line.amount, -150)
        self.old_analytic_line.write({"time_type_id": self.project_type_fixed_rule.id})
        self.assertEqual(self.old_analytic_line.amount, -20)
        self.old_analytic_line.write({"time_type_id": self.project_type_ratio_rule.id})
        self.assertEqual(self.old_analytic_line.amount, -225)
        self.old_analytic_line.write(
            {"time_type_id": self.project_type_domain_mix_rule.id}
        )
        self.assertEqual(self.old_analytic_line.amount, -20)

    def test_03_validation_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.env["project.time.type"].create(
                {
                    "name": "Validation error fix",
                    "apply_cost_rules": True,
                    "cost_rule_ids": [
                        (
                            0,
                            0,
                            {
                                "sequence": 1,
                                "cost_rule_type": "fixed",
                                "fixed_cost": 10,
                            },
                        )
                    ],
                }
            )
        with self.assertRaises(exceptions.ValidationError):
            self.env["project.time.type"].create(
                {
                    "name": "Validation error ratio",
                    "apply_cost_rules": True,
                    "cost_rule_ids": [
                        (
                            0,
                            0,
                            {
                                "sequence": 1,
                                "cost_rule_type": "ratio",
                                "ratio_value": -1.5,
                            },
                        )
                    ],
                }
            )
