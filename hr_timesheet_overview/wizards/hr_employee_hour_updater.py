# Copyright 2023 Camptocamp SA
import logging

from odoo import fields, models
from odoo.osv import expression

from ..helpers import get_attendances_values_by_date

_logger = logging.getLogger(__name__)


class WizardHrEmployeeHourUpdater(models.TransientModel):
    _name = "wizard.hr.employee.hour.updater"
    _description = "Allow to update HR Employee hours"

    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
        default=lambda self: self.env.user.employee_id,
    )
    date_from = fields.Date(
        "Start date", default=fields.Date.context_today, required=True
    )
    date_to = fields.Date("End date", default=fields.Date.context_today, required=True)
    timesheet_hours = fields.Boolean("Timesheet hours", default=True)
    contract_hours = fields.Boolean("Contract hours", default=True)

    def search_timesheet_domain(self):
        """Search filter rules for allocations"""
        base_domain = [("employee_id", "in", self.employee_ids.ids)]
        date_domain = expression.AND(
            [
                [("date", ">=", self.date_from)],
                [("date", "<=", self.date_to)],
            ]
        )
        domain = expression.AND([base_domain, date_domain])
        return domain

    def prepare_values(self):
        """Return a list of dict with computed values for this employee"""
        values = []
        if self.timesheet_hours:
            aal_model = self.env["account.analytic.line"]
            search_domain = self.search_timesheet_domain()
            timesheets = aal_model.search(search_domain)
            _logger.info(f"will process {len(timesheets)} timesheet lines")
            values.extend(timesheets.prepare_hr_employee_hour_values())
        if self.contract_hours:
            attendances_by_date = self.env.context.get("attendances_by_date")
            if not attendances_by_date:
                attendances_by_date = get_attendances_values_by_date(
                    self.employee_ids, self.date_from, self.date_to
                )
            for emp_vals in attendances_by_date.values():
                if not emp_vals:
                    continue
                assert self.date_from <= min(emp_vals)
                assert self.date_to >= max(emp_vals)
                values.extend(emp_vals.values())
        return values

    def action_submit(self):
        if not self.employee_ids:
            self.employee_ids = self.env["hr.employee"].search([])
        # Preloading all the needed attendances for days and hours quantities
        # It's really time consuming depending of employees and dates selection
        # But not as much as timesheets calculation
        attendances_by_date = get_attendances_values_by_date(
            self.employee_ids, self.date_from, self.date_to
        )
        values = self.with_context(
            attendances_by_date=attendances_by_date, active_test=False
        ).prepare_values()
        records = (
            self.env["hr.employee.hour"]
            .with_context(active_test=False)
            .create_or_update(values)
        )

        return {
            "type": "ir.actions.act_window",
            "name": "Updated HR Employee hours",
            "view_mode": "tree",
            "res_model": "hr.employee.hour",
            "domain": [("id", "in", records.ids)],
            "target": "current",
        }
