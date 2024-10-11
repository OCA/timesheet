# Copyright 2015 Camptocamp SA - Guewen Baconnier
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import exceptions, fields
from odoo.tests import common


class TestBeginEnd(common.TransactionCase):
    def setUp(self):
        super(TestBeginEnd, self).setUp()
        self.timesheet_line_model = self.env["account.analytic.line"]
        self.project = self.env.ref("project.project_project_1")
        self.employee = self.env.ref("hr.employee_qdp")
        self.base_line = {
            "name": "test",
            "date": fields.Date.today(),
            "time_start": 10.0,
            "time_stop": 12.0,
            "unit_amount": 2.0,
            "project_id": self.project.id,
            "employee_id": self.employee.id,
        }

    def test_compute_unit_amount(self):
        line = self.base_line.copy()
        del line["unit_amount"]
        line_record = self.timesheet_line_model.create(line)
        self.assertEqual(line_record.unit_amount, 2)
        line_record.time_stop = 14.0
        self.assertEqual(line_record.unit_amount, 4)

    def test_compute_unit_amount_no_compute_if_no_times(self):
        line = self.base_line.copy()
        del line["time_start"]
        del line["time_stop"]
        line_record = self.timesheet_line_model.create(line)
        self.assertEqual(line_record.unit_amount, 2.0)
        line_record.unit_amount = 3.0
        self.assertEqual(line_record.unit_amount, 3.0)

    def test_compute_unit_amount_to_zero(self):
        line = self.base_line.copy()
        del line["unit_amount"]
        line_record = self.timesheet_line_model.create(line)
        self.assertEqual(line_record.unit_amount, 2)
        line_record.write({"time_start": 0, "time_stop": 0})
        self.assertEqual(line_record.unit_amount, 0)

    def test_compute_unit_amount_to_zero_no_record(self):
        # Cannot create/save this model because it breaks a constraint, so using
        # .new().
        line = self.timesheet_line_model.new(
            {"name": "test", "time_start": 13.0, "time_stop": 12.0}
        )
        self.assertEqual(line.unit_amount, 0)
        line.time_stop = 10.0
        self.assertEqual(line.unit_amount, 0)

    def test_check_begin_before_end(self):
        line = self.base_line.copy()
        line.update({"time_start": 12.0, "time_stop": 10.0})
        with self.assertRaises(exceptions.ValidationError):
            self.timesheet_line_model.create(line)

    def test_check_wrong_duration(self):
        message_re = (
            r"The duration \(\d\d:\d\d\) must be equal to the "
            r"difference between the hours \(\d\d:\d\d\)\."
        )
        line = self.base_line.copy()
        line.update({"time_start": 10.0, "time_stop": 12.0, "unit_amount": 5.0})
        with self.assertRaisesRegex(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line)

    def test_check_overlap(self):
        line1 = self.base_line.copy()
        line1.update({"time_start": 10.0, "time_stop": 12.0, "unit_amount": 2.0})
        line2 = self.base_line.copy()
        line2.update({"time_start": 12.0, "time_stop": 14.0, "unit_amount": 2.0})
        self.timesheet_line_model.create(line1)
        self.timesheet_line_model.create(line2)

        message_re = r"overlap"

        line3 = self.base_line.copy()

        line3.update({"time_start": 9.0, "time_stop": 11, "unit_amount": 2.0})
        with self.assertRaisesRegex(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)

        line3.update({"time_start": 13.0, "time_stop": 15, "unit_amount": 2.0})
        with self.assertRaisesRegex(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)

        line3.update({"time_start": 8.0, "time_stop": 15, "unit_amount": 7.0})
        with self.assertRaisesRegex(exceptions.ValidationError, message_re):
            self.timesheet_line_model.create(line3)

    def test_check_precision(self):
        line1 = self.base_line.copy()
        line1.update({"time_start": 19.0, "time_stop": 20.314, "unit_amount": 1.314})
        self.timesheet_line_model.create(line1)
