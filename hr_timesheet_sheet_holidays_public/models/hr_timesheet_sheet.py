# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Sheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    hours_on_public_holiday = fields.Boolean(
        compute="_compute_hours_on_public_holiday",
        default=False,
        help="The employee has imputed hours on a public holiday.",
    )

    def _compute_hours_on_public_holiday(self):
        for sheet in self:
            sheet.hours_on_public_holiday = False
            holidays_list = self.env["hr.holidays.public"].get_holidays_list(
                start_dt=sheet.date_start,
                end_dt=sheet.date_end,
                employee_id=sheet.employee_id.id,
            )

            for holiday in holidays_list:
                if any(
                    line.unit_amount != 0.0
                    and not (line.holiday_id or line.global_leave_id)
                    and line.date == holiday.date
                    for line in sheet.timesheet_ids
                ):
                    sheet.hours_on_public_holiday = True
