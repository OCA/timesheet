# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from ..helpers import generate_dates_from_range, get_end_of_day


class Contract(models.Model):
    _name = "hr.contract"
    _inherit = ["hr.contract", "hr.employee.hour.mixin"]

    def prepare_hr_employee_hour_values(
        self, *, date_start=None, date_end=None, exclude_global_leaves=True, **kwargs
    ):
        model_id = self._get_model_id()
        values_list = []
        for contract in self:
            ranged_dates = generate_dates_from_range(
                date_start or contract.date_start, date_end or contract.date_end
            )
            calendar = contract.resource_calendar_id
            for date in ranged_dates:
                attendances = calendar.attendance_ids.filtered(
                    lambda att: int(att.dayofweek) == date.weekday()
                )
                if not attendances:
                    continue
                # Here, we MUST use datetime as some global leaves are based
                # on the previous day at 23h mostly
                end_of_day = get_end_of_day(date, attendances)
                global_leaves = calendar.global_leave_ids.filtered(
                    lambda gl: gl.date_from <= end_of_day <= gl.date_to
                )
                # We only take valid days of work
                if exclude_global_leaves and global_leaves:
                    continue
                time_qty = calendar.get_time_quantities(date=date)
                values_list.append(
                    {
                        "model_id": model_id,
                        "res_id": contract.id,
                        "name_id": f"{contract._name},{contract.id}",
                        "type": "contract",
                        "date": date,
                        "employee_id": contract.employee_id.id,
                        "hours_qty": time_qty["hours_qty"],
                        "days_qty": time_qty["days_qty"],
                    }
                )
        return values_list
