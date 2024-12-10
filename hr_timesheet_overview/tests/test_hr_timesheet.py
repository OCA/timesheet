# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from .common import (
    CURRENT_TIMESHEET_HEH_LINES_LENGTH as timesheet_oracle,
    HrDashboardCommon,
)


@freeze_time("2022-02-01")
class HrTimesheetTests(HrDashboardCommon):
    def test_create_employee_hours_from_timesheet(self):
        heh_lines = self._get_related_hours(self.timesheets)
        self.assertEqual(timesheet_oracle, len(heh_lines))
        self.assertEqual(timesheet_oracle * 7, sum(heh_lines.mapped("hours_qty")))
        self.assertEqual(24.0, round(sum(heh_lines.mapped("days_qty")), 4))

    def test_update_employee_hours_from_timesheet(self):
        new_hours = 11.81
        self.timesheets.write({"unit_amount": new_hours})
        heh_lines = self._get_related_hours(self.timesheets)
        self.assertEqual(timesheet_oracle, len(heh_lines))
        self.assertEqual(
            new_hours * timesheet_oracle, sum(heh_lines.mapped("hours_qty"))
        )
        self.assertEqual(40.4914, round(sum(heh_lines.mapped("days_qty")), 4))

    def test_delete_employee_hours_from_timesheet(self):
        deleted_ids = self.timesheets.ids
        self.timesheets.unlink()
        heh_lines = self._get_related_hours(self.timesheets, deleted_ids)
        self.assertEqual(0, len(heh_lines))

    def test_timesheet_without_employee_should_not_return_employee_hour(self):
        values = self.timesheets_without_employee.prepare_hr_employee_hour_values()
        self.assertEqual([], values)

    def test_prepare_hr_employee_hour_values_should_always_return_a_list(self):
        values = self.env["account.analytic.line"].prepare_hr_employee_hour_values()
        self.assertEqual([], values)
