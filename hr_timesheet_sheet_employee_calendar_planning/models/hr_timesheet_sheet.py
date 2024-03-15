# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from pytz import utc

from odoo import fields, models


class Sheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    invalid_hours_per_day = fields.Boolean(
        compute="_compute_invalid_imputations",
        default=False,
        help="The employee's imputed hours for one or more days differ from "
        "its theoretical hours for those days.",
    )
    invalid_hours_per_week = fields.Boolean(
        compute="_compute_invalid_imputations",
        default=False,
        help="The employee's imputed hours for a whole week differ from its "
        "theoretical hours for that week.",
    )
    hours_no_working_day = fields.Boolean(
        compute="_compute_invalid_imputations",
        default=False,
        help="The employee has imputed hours on a day where they're not "
        "supposed to work.",
    )

    def _compute_invalid_imputations(self):
        for sheet in self:
            theoretical_weekly_hours = sheet._calculate_theoretical_hours()
            real_weekly_hours = sheet._calculate_real_hours()

            sheet.invalid_hours_per_day = False
            sheet.hours_no_working_day = False
            sheet.invalid_hours_per_week = False

            for week_index in range(len(real_weekly_hours)):
                for weekday_index in range(7):
                    if (
                        theoretical_weekly_hours[week_index][weekday_index]
                        != real_weekly_hours[week_index][weekday_index]
                    ):
                        sheet.invalid_hours_per_day = True
                        if theoretical_weekly_hours[week_index][weekday_index] == 0:
                            sheet.hours_no_working_day = True
                if sum(theoretical_weekly_hours[week_index].values()) != sum(
                    real_weekly_hours[week_index].values()
                ):
                    sheet.invalid_hours_per_week = True

    def _calculate_theoretical_hours(self):
        """Get number of theoretical hours for each day in the sheet.
        We work with complete weeks, so if a timesheet ends on Friday we will get
        0 hours for Saturday and Sunday. To compute them, we use the employee's
        personal resource_calendar in the sheet's time span."""
        self.ensure_one()
        monday1, week_num = self.get_sheet_weeks_num()
        theoretical_weekly_hours = {
            week: {index: 0 for index in range(7)} for week in range(week_num)
        }

        employee = self.employee_id
        calendar = employee.resource_calendar_id
        start_date = datetime.combine(self.date_start, datetime.min.time()).replace(
            tzinfo=utc
        )
        end_date = datetime.combine(self.date_end, datetime.max.time()).replace(
            tzinfo=utc
        )
        intervals = calendar._work_intervals_batch(
            start_date, end_date, employee.resource_id, compute_leaves=True
        )

        for start, stop, _meta in intervals[employee.resource_id.id]:
            date = start.date()
            week = (date - monday1).days // 7
            weekday = date.weekday()
            hours_sum = (stop - start).total_seconds() / 3600
            theoretical_weekly_hours[week][weekday] += hours_sum

        return theoretical_weekly_hours

    def _calculate_real_hours(self):
        """Get number of real hours for each day in the sheet. We work with complete weeks,
        so if a timesheet ends on Friday we will get 0 hours for Saturday and Sunday."""
        self.ensure_one()
        monday1, week_num = self.get_sheet_weeks_num()
        real_weekly_hours = {
            week: {index: 0 for index in range(7)} for week in range(week_num)
        }

        for line in self.timesheet_ids:
            day_of_week = line.date.weekday()
            week = (line.date - monday1).days // 7
            if hasattr(line, "holiday_id") and hasattr(line, "global_leave_id"):
                if not line.holiday_id and not line.global_leave_id:
                    real_weekly_hours[week][day_of_week] += line.unit_amount
            else:
                real_weekly_hours[week][day_of_week] += line.unit_amount
        return real_weekly_hours

    def get_sheet_weeks_num(self):
        """Get number of weeks between sheet's date_start and date_end. Weeks start on
        Monday and end on Sunday.
        Example: If the sheet goes from Friday to next Monday, that counts as
        2 weeks (since the dates belong to 2 different weeks)."""
        self.ensure_one()
        dt1 = self.date_start
        dt2 = self.date_end
        monday1 = dt1 - timedelta(days=dt1.weekday())
        monday2 = dt2 - timedelta(days=dt2.weekday())
        return monday1, (monday2 - monday1).days // 7 + 1
