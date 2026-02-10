# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _check_can_write(self, values):
        # A holiday generated timesheet can only be modified if holiday type
        # allows it for everybody, or if the user is an approver
        obj = self
        holiday = self.sudo().holiday_id
        if (
            holiday
            and (
                holiday.holiday_status_id.timesheet_edit_level == "all"
                or (
                    holiday.holiday_status_id.timesheet_edit_level == "approver"
                    and self.env.user.has_group("hr_holidays.group_hr_holidays_user")
                )
            )
            and (not set(values.keys()) - set(self._get_ts_from_holiday_edit_fields()))
        ):
            obj = self.sudo()
        return super(AccountAnalyticLine, obj)._check_can_write(values)

    @api.model
    def _get_ts_from_holiday_edit_fields(self):
        return ["name", "unit_amount"]
