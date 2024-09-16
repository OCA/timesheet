# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import exceptions, fields
from odoo.tests.common import TransactionCase


class TestBeginEndNoEnd(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env.ref("project.project_project_1")
        self.employee = self.env.ref("hr.employee_qdp")

    def base_line(self):
        return {
            "name": "test",
            "date": fields.Date.today(),
            "time_start": 10.0,
            "time_stop": 12.0,
            "unit_amount": 2.0,
            "project_id": self.project.id,
            "employee_id": self.employee.id,
        }

    def test_check_end_is_zero(self):
        line = self.base_line()
        line.update({"time_stop": 0})
        # No error.
        self.env["account.analytic.line"].create(line)

    def test_check_end_is_not_zero(self):
        line = self.base_line()
        line_record = self.env["account.analytic.line"].create(line)
        with self.assertRaises(exceptions.ValidationError):
            line_record.time_stop = 1

    def test_check_end_is_not_zero_no_record(self):
        line = self.base_line()
        line.update({"time_stop": 1, "unit_amount": 0})
        with self.assertRaises(exceptions.ValidationError):
            self.env["account.analytic.line"].create(line)

    def test_no_overlap(self):
        line_1 = self.base_line()
        line_1.update({"time_stop": 0, "unit_amount": 0})
        line_2 = line_1.copy()
        line_2.update({"time_start": 11.0, "unit_amount": 1})
        line_3 = self.base_line()
        # Able to create all without overlap, because time_stop is 0 for two of
        # them, and they don't count, even though their start times are
        # overlapped with line_3.
        self.env["account.analytic.line"].create([line_1, line_2, line_3])
