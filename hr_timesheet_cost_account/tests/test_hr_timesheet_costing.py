# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrTimesheetCosting(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.account_model = cls.env["account.account"]
        cls.journal_model = cls.env["account.journal"]
        cls.project_model = cls.env["project.project"]
        cls.employee_model = cls.env["hr.employee"]
        cls.timesheet_model = cls.env["account.analytic.line"]
        cls.costing_model = cls.env["hr.timesheet.costing"]

        cls.journal = cls.journal_model.search(
            [("type", "=", "general"), ("company_id", "=", cls.company.id)],
            limit=1,
        )
        cls.project = cls.project_model.create({"name": "Test Project"})
        cls.project2 = cls.project_model.create({"name": "Test Project 2"})

        cls.employee = cls.employee_model.create(
            {"name": "Test Employee", "hourly_cost": 100.0}
        )
        cls.employee2 = cls.employee_model.create(
            {"name": "Test Employee 2", "hourly_cost": 80.0}
        )
        cls.costing = cls.costing_model.create(
            {
                "date_from": "2026-01-01",
                "date_to": "2026-01-31",
                "journal_id": cls.journal.id,
            }
        )

        cls.ts1 = cls.timesheet_model.create(
            {
                "name": "Test work",
                "project_id": cls.project.id,
                "employee_id": cls.employee.id,
                "unit_amount": 8.0,
                "date": "2026-01-15",
            }
        )
        cls.ts2 = cls.timesheet_model.create(
            {
                "name": "Test work",
                "project_id": cls.project.id,
                "employee_id": cls.employee.id,
                "unit_amount": 4.0,
                "date": "2026-01-15",
            }
        )
        cls.ts3 = cls.timesheet_model.create(
            {
                "name": "Test work",
                "project_id": cls.project2.id,
                "employee_id": cls.employee.id,
                "unit_amount": 8.0,
                "date": "2026-01-15",
            }
        )
        cls.ts4 = cls.timesheet_model.create(
            {
                "name": "Test work",
                "project_id": cls.project.id,
                "employee_id": cls.employee2.id,
                "unit_amount": 8.0,
                "date": "2026-01-15",
            }
        )
        cls.cost_account = cls.account_model.create(
            {"name": "TS Cost", "code": "TSC99", "account_type": "expense"}
        )
        cls.suspense_account = cls.account_model.create(
            {
                "name": "TS Suspense",
                "code": "TSS99",
                "account_type": "liability_current",
            }
        )
        # Config company
        cls.company.write(
            {
                "timesheet_cost_account_id": cls.cost_account.id,
                "timesheet_suspense_account_id": cls.suspense_account.id,
            }
        )

    def test_01_check_constraint(self):
        # Date Constraint
        with self.assertRaisesRegex(
            ValidationError,
            "Date From must be earlier than or equal to Date To.",
        ):
            self.env["hr.timesheet.costing"].create(
                {
                    "date_from": "2026-01-31",
                    "date_to": "2026-01-01",
                    "journal_id": self.journal.id,
                }
            )
        # No Lines
        with self.assertRaisesRegex(
            UserError, "Please fetch timesheets before confirming."
        ):
            self.costing.action_confirm()

    def test_02_get_timesheet(self):
        # No filter, Get all timesheet
        self.assertEqual(len(self.costing.timesheet_ids), 0)
        self.costing.action_get_timesheets()
        self.assertEqual(len(self.costing.timesheet_ids), 4)

        # Get only project, it should be 3
        self.costing.project_ids = self.project
        self.costing.action_get_timesheets()
        self.assertEqual(len(self.costing.timesheet_ids), 3)

        # Get only project and employee, it should be 2
        self.costing.employee_ids = self.employee
        self.costing.action_get_timesheets()
        self.assertEqual(len(self.costing.timesheet_ids), 2)

    def test_03_create_jv_auto_post(self):
        self.assertEqual(self.costing.state, "draft")
        self.assertTrue(self.costing.auto_post)
        self.assertEqual(len(self.costing.timesheet_ids), 0)
        self.costing.action_get_timesheets()
        # Get all timesheet
        self.assertEqual(len(self.costing.timesheet_ids), 4)
        self.assertEqual(self.costing.amount_total, -2640.0)  # 800 + 400 + 800 + 640

        self.costing.action_confirm()
        self.assertEqual(self.costing.state, "confirmed")

        # Confirm without config
        self.costing.company_id.timesheet_cost_account_id = False
        with self.assertRaisesRegex(
            UserError,
            "Please configure Cost Account and Suspense Account"
            " in Accounting Settings.",
        ):
            self.costing.action_create_jv()

        self.assertFalse(self.costing.move_id)
        self.costing.company_id.timesheet_cost_account_id = self.cost_account.id
        self.costing.action_create_jv()
        # Move Created
        self.assertEqual(self.costing.state, "done")
        move = self.costing.move_id
        self.assertTrue(move)
        self.assertEqual(move.state, "posted")
        amount_total = abs(self.costing.amount_total)
        self.assertEqual(move.amount_total, amount_total)
        self.assertEqual(
            sum(
                move.line_ids.filtered(
                    lambda line: line.account_id.id == self.cost_account.id
                ).mapped("debit")
            ),
            amount_total,
        )
        self.assertEqual(
            sum(
                move.line_ids.filtered(
                    lambda line: line.account_id.id == self.suspense_account.id
                ).mapped("credit")
            ),
            amount_total,
        )
        # Move link to timesheet costing
        action = move.action_view_timesheet_costing()
        self.assertEqual(action["res_id"], self.costing.id)

        # Timesheet link to move
        action = self.costing.action_view_move()
        self.assertEqual(action["res_id"], move.id)

        # Try delete Timesheet
        with self.assertRaisesRegex(
            UserError,
            "Cannot delete Timesheet Costing in Confirmed or Done state.",
        ):
            self.costing.unlink()

        # Try reset draft after created move
        with self.assertRaisesRegex(
            UserError, "Cannot reset: a Journal Entry is linked."
        ):
            self.costing.action_reset_draft()

        # Remove move
        move.button_draft()
        self.assertEqual(move.state, "draft")
        move.unlink()
        self.assertFalse(self.costing.move_id)

    def test_04_create_jv_draft(self):
        self.costing.auto_post = False
        self.assertEqual(self.costing.state, "draft")
        self.assertFalse(self.costing.can_reset_to_draft)
        self.assertFalse(self.costing.auto_post)
        self.assertEqual(len(self.costing.timesheet_ids), 0)
        self.costing.action_get_timesheets()
        # Get all timesheet
        self.assertEqual(len(self.costing.timesheet_ids), 4)
        self.assertEqual(self.costing.amount_total, -2640.0)  # 800 + 400 + 800 + 640

        self.costing.action_confirm()
        self.assertEqual(self.costing.state, "confirmed")
        self.assertTrue(self.costing.can_reset_to_draft)

        self.costing.action_reset_draft()
        self.assertEqual(self.costing.state, "draft")

        self.costing.action_confirm()
        self.assertEqual(self.costing.state, "confirmed")

        self.costing.action_create_jv()
        # Move Created
        self.assertEqual(self.costing.state, "done")
        self.assertFalse(self.costing.can_reset_to_draft)
        move = self.costing.move_id
        amount_total = abs(self.costing.amount_total)
        self.assertTrue(move)
        self.assertEqual(move.state, "draft")
        self.assertEqual(move.amount_total, amount_total)
        self.assertEqual(
            sum(
                move.line_ids.filtered(
                    lambda line: line.account_id.id == self.cost_account.id
                ).mapped("debit")
            ),
            amount_total,
        )
        self.assertEqual(
            sum(
                move.line_ids.filtered(
                    lambda line: line.account_id.id == self.suspense_account.id
                ).mapped("credit")
            ),
            amount_total,
        )
        # Remove move
        move.unlink()
        self.assertFalse(self.costing.move_id)
        # Reset costing
        self.costing.action_reset_draft()
        self.assertEqual(self.costing.state, "draft")

        self.costing.action_cancel()
        self.assertEqual(self.costing.state, "cancelled")

        self.costing.unlink()

    def test_05_groupby_project(self):
        self.costing.write(
            {
                "group_by_project": True,
                "group_by_employee": False,
            }
        )
        self.costing.action_get_timesheets()
        self.costing.action_confirm()
        self.costing.action_create_jv()
        move = self.costing.move_id

        # 2 projects -> 2 debit lines + 1 credit line = 3 lines
        self.assertEqual(len(move.line_ids), 3)
        debit_lines = move.line_ids.filtered(lambda line: line.debit > 0)
        self.assertEqual(len(debit_lines), 2)

        # Project 1: ts1 (800) + ts2 (400) + ts4 (640) = 1840
        # Project 2: ts3 (800) = 800
        proj1_line = debit_lines.filtered(lambda line: line.name == self.project.name)
        proj2_line = debit_lines.filtered(lambda line: line.name == self.project2.name)
        self.assertEqual(proj1_line.debit, 1840.0)
        self.assertEqual(proj2_line.debit, 800.0)
        self.assertEqual(sum(move.line_ids.mapped("credit")), 2640.0)

    def test_06_groupby_employee(self):
        self.costing.write(
            {
                "group_by_project": False,
                "group_by_employee": True,
            }
        )
        self.costing.action_get_timesheets()
        self.costing.action_confirm()
        self.costing.action_create_jv()
        move = self.costing.move_id

        # 2 employees -> 2 debit lines + 1 credit line = 3 lines
        self.assertEqual(len(move.line_ids), 3)
        debit_lines = move.line_ids.filtered(lambda line: line.debit > 0)
        self.assertEqual(len(debit_lines), 2)

        # Employee 1: ts1 (800) + ts2 (400) + ts3 (800) = 2000
        # Employee 2: ts4 (640) = 640
        emp1_line = debit_lines.filtered(lambda line: line.name == self.employee.name)
        emp2_line = debit_lines.filtered(lambda line: line.name == self.employee2.name)
        self.assertEqual(emp1_line.debit, 2000.0)
        self.assertEqual(emp2_line.debit, 640.0)
        self.assertEqual(sum(move.line_ids.mapped("credit")), 2640.0)

    def test_07_groupby_project_employee(self):
        self.costing.write(
            {
                "group_by_project": True,
                "group_by_employee": True,
            }
        )
        self.costing.action_get_timesheets()
        self.costing.action_confirm()
        self.costing.action_create_jv()
        move = self.costing.move_id

        # 3 groups -> 3 debit lines + 1 credit line = 4 lines
        self.assertEqual(len(move.line_ids), 4)
        debit_lines = move.line_ids.filtered(lambda line: line.debit > 0)
        self.assertEqual(len(debit_lines), 3)

        # Project 1 / Employee 1: ts1 (800) + ts2 (400) = 1200
        # Project 2 / Employee 1: ts3 (800) = 800
        # Project 1 / Employee 2: ts4 (640) = 640
        label_p1_e1 = f"{self.project.name} / {self.employee.name}"
        label_p2_e1 = f"{self.project2.name} / {self.employee.name}"
        label_p1_e2 = f"{self.project.name} / {self.employee2.name}"

        line_p1_e1 = debit_lines.filtered(lambda line: line.name == label_p1_e1)
        line_p2_e1 = debit_lines.filtered(lambda line: line.name == label_p2_e1)
        line_p1_e2 = debit_lines.filtered(lambda line: line.name == label_p1_e2)

        self.assertEqual(line_p1_e1.debit, 1200.0)
        self.assertEqual(line_p2_e1.debit, 800.0)
        self.assertEqual(line_p1_e2.debit, 640.0)
        self.assertEqual(sum(move.line_ids.mapped("credit")), 2640.0)
