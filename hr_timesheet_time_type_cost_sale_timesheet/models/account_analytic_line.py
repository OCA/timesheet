# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _hourly_cost(self):
        """Apply the time type cost to the employee-rate mapped cost.

        ``sale_timesheet`` returns the mapped cost without calling ``super()``,
        so the time type rule of ``hr_timesheet_time_type_cost`` never runs on
        employee-rate projects. This module is loaded after ``sale_timesheet``
        and therefore sits above it in the MRO: it resolves the mapped cost and
        hands it to the time type rule, and defers to ``super()`` on every other
        project.
        """
        self.ensure_one()
        if self.project_id.pricing_type == "employee_rate":
            mapping_entry = self._get_employee_mapping_entry()
            if mapping_entry:
                return self._apply_time_type_cost(mapping_entry.cost)
        return super()._hourly_cost()
