# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from freezegun import freeze_time

from .common import (
    CLOSE_CONTRACT_HEH_LINES_LENGTH,
    CURRENT_CONTRACT_HEH_LINES_LENGTH,
    HrDashboardCommon,
)


@freeze_time("2022-02-01")
class HrContractTests(HrDashboardCommon):
    def test_create_employee_hours_from_current_contract(self):
        heh_lines = self._get_related_hours(self.current_contract)
        self.assertEqual(CURRENT_CONTRACT_HEH_LINES_LENGTH, len(heh_lines))

    def test_create_employee_hours_from_close_contract(self):
        heh_lines = self._get_related_hours(self.close_contract)
        self.assertEqual(CLOSE_CONTRACT_HEH_LINES_LENGTH, len(heh_lines))

    def test_update_employee_hours_from_current_contract(self):
        # We remove 9 days from start date (5 work days)
        minus_days = 5
        self.current_contract.write({"date_start": datetime(2022, 1, 10).date()})
        heh_lines = self._get_related_hours(self.current_contract)
        oracle = CURRENT_CONTRACT_HEH_LINES_LENGTH - minus_days
        self.assertEqual(oracle, len(heh_lines))

    def test_update_employee_hours_from_close_contract(self):
        # We add 8 days to end date (4 work days)
        # And we add 9 days to current contract start (5 work days)
        added_days = 4
        # needed to avoid contract overlap
        self.current_contract.write({"date_start": datetime(2022, 1, 10).date()})
        self.close_contract.write({"date_end": datetime(2022, 1, 9).date()})
        heh_lines = self._get_related_hours(self.close_contract)
        oracle = CLOSE_CONTRACT_HEH_LINES_LENGTH + added_days
        self.assertEqual(oracle, len(heh_lines))

    def test_delete_employee_hours_from_current_contract(self):
        deleted_id = self.current_contract.id
        self.current_contract.unlink()
        heh_lines = self._get_related_hours(self.current_contract, [deleted_id])
        self.assertEqual(0, len(heh_lines))

    def test_delete_employee_hours_from_close_contract(self):
        deleted_id = self.close_contract.id
        self.close_contract.unlink()
        heh_lines = self._get_related_hours(self.close_contract, [deleted_id])
        self.assertEqual(0, len(heh_lines))

    def test_prepare_hr_employee_hour_values_should_always_return_a_list(self):
        values = self.env["hr.contract"].prepare_hr_employee_hour_values()
        self.assertEqual([], values)
