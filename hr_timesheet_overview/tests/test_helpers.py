# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.tools import mute_logger

from odoo.addons.hr_timesheet_overview.helpers import get_attendances_values_by_date

from .common import (
    CLOSE_CONTRACT_HEH_LINES_LENGTH,
    CURRENT_CONTRACT_HEH_LINES_LENGTH,
    HrDashboardCommon,
)


@freeze_time("2022-02-01")
class HrEmployeeHourTests(HrDashboardCommon):
    def test_get_attendances_values_by_date_with_valid_contract(self):
        values = get_attendances_values_by_date(self.employee)
        oracle = CURRENT_CONTRACT_HEH_LINES_LENGTH + CLOSE_CONTRACT_HEH_LINES_LENGTH
        self.assertEqual(oracle, len(values[self.employee.id]))

    def test_get_attendances_values_by_date_with_no_contract(self):
        # First purge all timesheets
        contracts = self.env["hr.contract"].search(
            [("employee_id", "=", self.employee.id)]
        )
        with mute_logger("odoo.models.unlink"):
            contracts.unlink()
        # Then get attendances
        values = get_attendances_values_by_date(self.employee)
        # Will only return an empty dict for this employee
        oracle = {self.employee.id: {}}
        self.assertEqual(oracle, values)
