# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _name = "account.analytic.line"
    _inherit = ["account.analytic.line", "hr.employee.hour.mixin"]

    def prepare_hr_employee_hour_values(self, **kwargs):
        """Prepare hr employee hours for each timesheet.

        Day ratio quantity is a percentage of consumed hours relative to the
        attendance day max quantity to make a full day (2h on 8h day is 25%).

        If `attendances_by_date` is not set in context or date is not found,
        default hours and day quantity are used
        """
        uom_hour = self.env.ref("uom.product_uom_hour")
        model_id = self._get_model_id()
        values_list = []
        cached_by_date = self.env.context.get("attendances_by_date")
        for timesheet in self.filtered("employee_id"):
            project = timesheet.project_id
            task = timesheet.task_id
            contract_hours, contract_day = self._contract_hours_day(
                timesheet.employee_id, timesheet.date, cache=cached_by_date
            )
            hours_qty = timesheet.unit_amount
            if timesheet.product_uom_id != uom_hour:
                try:
                    hours_qty = timesheet.product_uom_id._compute_quantity(
                        timesheet.unit_amount, uom_hour, round=False
                    )
                except Exception as e:
                    # Sometimes, the unit of measure is not properly defined
                    # and can lead to impossible conversion.
                    # Instead of blocking lots of other lines to be processed
                    # Inform by log and pursuit
                    _logger.error(e)

            # Get the day filled ratio
            # If attendance hours qty is empty, it is an extra work day
            days_qty = hours_qty / contract_hours
            # If hours filled the day then prefer to get ratio from the conf
            # To avoid setting a full day if conf says half one only
            if days_qty == 1:
                days_qty = contract_day
            values_list.append(
                {
                    "model_id": model_id,
                    "res_id": timesheet.id,
                    "name_id": f"{timesheet._name},{timesheet.id}",
                    "type": "timesheet",
                    "date": timesheet.date,
                    "employee_id": timesheet.employee_id.id,
                    "project_id": project.id,
                    "task_id": task.id,
                    "analytic_group_id": timesheet.group_id.id,
                    "hours_qty": hours_qty,
                    "days_qty": days_qty,
                }
            )
        return values_list
