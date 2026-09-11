# Copyright 2015 Camptocamp SA - Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import exceptions, fields
from odoo.tests import common


class TestBeginEndBreak(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.timesheet_line_model = cls.env["account.analytic.line"]
        cls.user = cls.env.ref("base.user_root")
        cls.employee = cls.env["hr.employee"].search(
            [("user_id", "=", cls.user.id)], limit=1
        )
        if not cls.employee:
            cls.employee = cls.env["hr.employee"].create(
                {"name": "Test Employee", "user_id": cls.user.id}
            )
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Departments", "default_applicability": "optional"}
        )
        cls.analytic = cls.env["account.analytic.account"].create(
            {
                "name": "Administrative",
                "plan_id": cls.analytic_plan.id,
                "company_id": False,
            }
        )
        cls.base_line = {
            "name": "test",
            "date": fields.Date.today(),
            "time_start": 10.0,
            "time_stop": 12.0,
            "user_id": cls.user.id,
            "employee_id": cls.employee.id,
            "unit_amount": 2.0,
            "account_id": cls.analytic.id,
        }

    def test_onchange(self):
        line = self.timesheet_line_model.new(
            {"name": "test", "time_start": 10.0, "time_stop": 12.0}
        )
        line.onchange_hours_start_stop()
        self.assertEqual(line.unit_amount, 2)

    def test_onchange_no_update(self):
        line = self.timesheet_line_model.new(
            {
                "name": "test",
                "time_start": 12.0,
                "time_stop": 12.0,
                "break_duration": 0.0,
            }
        )
        line.onchange_hours_start_stop()
        self.assertEqual(line.unit_amount, 0)

    def test_check_begin_before_end(self):
        line = self.base_line.copy()
        line.update({"time_start": 12.0, "time_stop": 10.0})
        with self.assertRaises(exceptions.ValidationError):
            self.timesheet_line_model.create(line)

    def test_check_wrong_duration(self):
        message_re = (
            r"The duration .* must be equal to the difference between the hours"
        )
        line = self.base_line.copy()
        line.update({"time_start": 10.0, "time_stop": 12.0, "unit_amount": 5.0})
        with self.assertRaisesRegex(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line)

    def test_check_overlap(self):
        line1 = self.base_line.copy()
        line1.update({"time_start": 10.0, "time_stop": 12.0, "unit_amount": 2.0})
        self.timesheet_line_model.create(line1)

        line2 = self.base_line.copy()
        line2.update({"time_start": 12.0, "time_stop": 14.0, "unit_amount": 2.0})
        self.timesheet_line_model.create(line2)

        message_re = r"overlap"
        line3 = self.base_line.copy()
        line3.update({"time_start": 9.0, "time_stop": 11.0, "unit_amount": 2.0})
        with self.assertRaisesRegex(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)

    def test_check_precision(self):
        line1 = self.base_line.copy()
        # Rounded to 2 decimals to avoid floating point issues
        line1.update({"time_start": 19.0, "time_stop": 20.31, "unit_amount": 1.31})
        self.timesheet_line_model.create(line1)

    def test_break_duration_calculation(self):
        vals = self.base_line.copy()
        vals.update(
            {
                "time_start": 8.0,
                "time_stop": 10.0,
                "break_duration": 0.5,
                "unit_amount": 1.5,
            }
        )
        line = self.timesheet_line_model.create(vals)
        self.assertEqual(line.unit_amount, 1.5)

    def test_onchange_with_break(self):
        line = self.timesheet_line_model.new(
            {"time_start": 8.0, "time_stop": 10.0, "break_duration": 0.5}
        )
        line.onchange_hours_start_stop()
        self.assertEqual(line.unit_amount, 1.5)

    def test_onchange_partial_hours(self):
        # Only the begin hour is set: unit_amount must stay untouched.
        line = self.timesheet_line_model.new(
            {"time_start": 8.0, "break_duration": 0.5, "unit_amount": 3.0}
        )
        line.onchange_hours_start_stop()
        self.assertEqual(line.unit_amount, 3.0)

    def test_onchange_stop_before_start(self):
        # Stop before start: unit_amount must not be recomputed.
        line = self.timesheet_line_model.new(
            {"time_start": 12.0, "time_stop": 10.0, "unit_amount": 4.0}
        )
        line.onchange_hours_start_stop()
        self.assertEqual(line.unit_amount, 4.0)

    def test_no_begin_end_skips_constraint(self):
        # A line without begin/end hours is a regular timesheet: no check.
        vals = self.base_line.copy()
        vals.update({"time_start": 0.0, "time_stop": 0.0, "unit_amount": 5.0})
        line = self.timesheet_line_model.create(vals)
        self.assertEqual(line.unit_amount, 5.0)

    def test_zero_duration_line(self):
        # Equal begin/end (zero worked hours) is allowed.
        vals = self.base_line.copy()
        vals.update({"time_start": 8.0, "time_stop": 8.0, "unit_amount": 0.0})
        line = self.timesheet_line_model.create(vals)
        self.assertEqual(line.unit_amount, 0.0)
