# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from ..helpers import DEFAULT_TIME_QTY, get_attendances_values_by_date


class HrEmployeeHourMixin(models.AbstractModel):
    _name = "hr.employee.hour.mixin"
    _description = "HR Employee Hour Mixin"

    @api.model
    def _get_model_id(self):
        return self.env["ir.model"]._get_id(self._name)

    @api.model
    def _contract_hours_day(self, employee, date_, cache=None):
        try:
            if cache:
                attendance = cache[employee.id][date_]
            else:
                attendance = get_attendances_values_by_date(
                    employee,
                    date_from=date_,
                    date_to=date_,
                )[employee.id][date_]
        except KeyError:
            attendance = DEFAULT_TIME_QTY

        hours_qty = attendance["hours_qty"] or DEFAULT_TIME_QTY["hours_qty"]
        days_qty = attendance["days_qty"]
        return (hours_qty, days_qty)

    def prepare_hr_employee_hour_values(self, **kwargs):
        """Return hr employee hour values
        :returns: a list of dicts
        """
        raise NotImplementedError("HR employee hours mixin implementation error!")

    def update_employee_hours(self, purge=True):
        """Regeneration of all related employee hours
        :param purge: boolean Removes all previous related employee hours
        """
        if purge:
            self.hook_unlink_employee_hours().unlink()
        heh_values = self.prepare_hr_employee_hour_values()
        return self.env["hr.employee.hour"].create_or_update(heh_values)

    def hook_unlink_employee_hours(self):
        """Purge HR employee hours"""
        heh_model = self.env["hr.employee.hour"].sudo().with_context(active_test=False)
        heh_domain = [("model_id.model", "=", self._name), ("res_id", "in", self.ids)]
        return heh_model.search(heh_domain)

    def unlink(self):
        self.hook_unlink_employee_hours().unlink()
        return super().unlink()

    def write(self, vals):
        result = super().write(vals)
        # In case of archiving only, avoid processing the whole regeneration
        if list(vals) == ["active"]:
            self.env["hr.employee.hour"].toggle_active_for_records(self)
        else:
            self.sudo().update_employee_hours()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        # Generate employee hours
        records = super().create(vals_list)
        records.sudo().update_employee_hours()
        return records
