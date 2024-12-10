# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from freezegun import freeze_time

from odoo.tools import mute_logger

from .common import (
    INVALID_DAYS_DEC_2021,
    TOTAL_HEH_LINES,
    VALID_DAYS_JAN_2022,
    HrDashboardCommon,
)


@freeze_time("2022-02-01")
class HrEmployeeHourTests(HrDashboardCommon):
    def test_global_employee_hours_pregenerate_action(self):
        heh_model = self.env["hr.employee.hour"]
        # Purge previous hours
        prev_heh_lines = heh_model.search([("employee_id", "=", self.employee.id)])
        oracle = TOTAL_HEH_LINES
        self.assertEqual(
            oracle,
            len(prev_heh_lines),
            f"The pre-generation of employee hours should give {oracle} lines,"
            f" not {len(prev_heh_lines)}.",
        )

    def test_global_employee_hours_generate_action_idempotent(self):
        heh_model = self.env["hr.employee.hour"]
        # Purge previous hours
        prev_heh_lines = heh_model.search([("employee_id", "=", self.employee.id)])
        oracle = len(prev_heh_lines)
        with mute_logger("odoo.models.unlink"):
            prev_heh_lines.unlink()
        # All possible dates (we can't rely on freeze_gun at this stage)
        heh_model.action_generate_data(
            self.employee.ids, date_to=datetime(2022, 2, 1).date()
        )
        heh_lines = self.env["hr.employee.hour"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertEqual(
            oracle,
            len(heh_lines),
            "This method 'generate_action' MUST be idempotent from initial"
            " generation.",
        )

    def test_global_employee_hours_generate_action_all_possible_dates(self):
        heh_model = self.env["hr.employee.hour"]
        # Purge previous hours
        prev_heh_lines = heh_model.search([("employee_id", "=", self.employee.id)])
        oracle = TOTAL_HEH_LINES
        with mute_logger("odoo.models.unlink"):
            prev_heh_lines.unlink()
        # All possible dates until desired freezed date
        heh_model.action_generate_data(
            self.employee.ids, date_to=datetime(2022, 2, 1).date()
        )
        heh_lines = self.env["hr.employee.hour"].search(
            [("employee_id", "=", self.employee.id)]
        )
        self.assertEqual(
            oracle,
            len(heh_lines),
            f"This employee {self.employee.name} should have {oracle}"
            " hr.employee.hour records defined.",
        )

    def test_global_employee_hours_generate_action_specific_date_to(self):
        heh_model = self.env["hr.employee.hour"]
        # Purge previous hours
        prev_heh_lines = heh_model.search([("employee_id", "=", self.employee.id)])
        with mute_logger("odoo.models.unlink"):
            prev_heh_lines.unlink()
        # Only a date to
        date_to = datetime(2022, 2, 20).date()
        heh_model.action_generate_data(self.employee.ids, date_to=date_to)
        heh_lines = self.env["hr.employee.hour"].search(
            [("employee_id", "=", self.employee.id)]
        )
        oracle = 74
        self.assertEqual(
            oracle,
            len(heh_lines),
            f"This employee {self.employee.name} should have {oracle}"
            ""
            f" hr.employee.hour records defined for a date_to={date_to}.",
        )

    def test_global_employee_hours_generate_action_invalid_ranged_dates(self):
        heh_model = self.env["hr.employee.hour"]
        # Purge previous hours
        prev_heh_lines = heh_model.search([("employee_id", "=", self.employee.id)])
        with mute_logger("odoo.models.unlink"):
            prev_heh_lines.unlink()
        # Ranged date
        date_from = datetime(2012, 1, 1).date()
        date_to = datetime(2013, 12, 31).date()
        heh_model.action_generate_data(
            [self.employee.id], date_from=date_from, date_to=date_to
        )
        heh_lines = self.env["hr.employee.hour"].search(
            [("employee_id", "=", self.employee.id)]
        )
        oracle = 0
        self.assertEqual(
            oracle,
            len(heh_lines),
            f"This ranged dates {date_from}/{date_to} should not generate any"
            " employee hour records.",
        )

    def test_prepare_attendance_value_for_unattended_dates(self):
        for week in INVALID_DAYS_DEC_2021:
            for day in week:
                unattended_date = datetime(2021, 12, day).date()
                values = self.close_contract.prepare_hr_employee_hour_values(
                    date_start=unattended_date, date_end=unattended_date
                )
                self.assertFalse(
                    values,
                    f"This unattended date {unattended_date} should not"
                    " generate an employee hour for this contract"
                    ""
                    f" {self.close_contract.name}",
                )

    def test_prepare_attendance_value_for_attendended_dates(self):
        ir_model = self.env["ir.model"].search(
            [("model", "=", self.current_contract._name)]
        )
        calendar = self.current_contract.resource_calendar_id
        for week in VALID_DAYS_JAN_2022:
            for day, days_qty in week:
                attended_date = datetime(2022, 1, day).date()
                date_attendances = calendar.attendance_ids.filtered(
                    lambda att: int(att.dayofweek) == attended_date.weekday()
                )
                hours_per_day_for_date = calendar._compute_hours_per_day(
                    date_attendances
                )
                oracle = {
                    "date": attended_date,
                    "days_qty": days_qty,
                    "employee_id": self.employee.id,
                    "hours_qty": hours_per_day_for_date,
                    "model_id": ir_model.id,
                    "res_id": self.current_contract.id,
                    "type": "contract",
                }
                values = self.current_contract.prepare_hr_employee_hour_values(
                    date_start=attended_date,
                    date_end=attended_date,
                    exclude_global_leaves=True,
                )
                self.assertEqual(
                    len(values),
                    1,
                )
                value = values[0]
                self.assertTrue(
                    value,
                    f"This attended date {attended_date} should generate an"
                    " employee hour for this contract"
                    f" {self.current_contract.name}",
                )
                self.assertEqual(oracle["date"], value["date"])
                self.assertEqual(oracle["days_qty"], round(value["days_qty"], 4))
                self.assertEqual(oracle["hours_qty"], value["hours_qty"])
                self.assertEqual(oracle["model_id"], value["model_id"])
                self.assertEqual(oracle["res_id"], value["res_id"])
                self.assertEqual(oracle["type"], value["type"])
                self.assertEqual(oracle["employee_id"], value["employee_id"])

    def test_prepare_timesheets_lines(self):
        timesheet_qty = len(self.timesheets.ids)
        values = self.timesheets.prepare_hr_employee_hour_values()
        timesheet_days_qty = sum(v["days_qty"] for v in values)
        timesheet_hours_qty = sum(v["hours_qty"] for v in values)
        self.assertEqual(timesheet_qty, len(values))
        self.assertEqual(24.0, timesheet_days_qty)
        self.assertEqual(21 * 7, timesheet_hours_qty)

    def test_contract_name_id(self):
        cc = self.current_contract
        heh_line = self.env["hr.employee.hour"].search(
            [("type", "=", "contract"), ("res_id", "=", cc.id)], limit=1
        )
        self.assertEqual(cc, heh_line.name_id)

    def test_timesheet_name_id(self):
        ts = self.timesheets[0]
        heh_line = self.env["hr.employee.hour"].search(
            [("type", "=", "timesheet"), ("res_id", "=", ts.id)], limit=1
        )
        self.assertEqual(ts, heh_line.name_id)

    def test_timesheet_project_id(self):
        ts = self.timesheets[0]
        heh_line = self.env["hr.employee.hour"].search(
            [("type", "=", "timesheet"), ("res_id", "=", ts.id)], limit=1
        )
        self.assertEqual(self.project, heh_line.project_id)

    def test_timesheet_task_id(self):
        ts = self.timesheets[0]
        heh_line = self.env["hr.employee.hour"].search(
            [("type", "=", "timesheet"), ("res_id", "=", ts.id)], limit=1
        )
        self.assertEqual(self.task, heh_line.task_id)
