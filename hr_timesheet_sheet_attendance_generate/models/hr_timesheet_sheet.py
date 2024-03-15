# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

import pytz

from odoo import _, models


class Sheet(models.Model):
    _inherit = "hr_timesheet.sheet"

    def button_generate_attendances(self):
        # Generate the missing attendances and let the user
        # choose whether they actually want them to be created
        self.ensure_one()
        generated_attendances = self.action_generate_attendances()
        if generated_attendances:
            form_view = self.env.ref(
                "hr_timesheet_sheet_attendance_generate."
                "view_generated_attendances_selection_form"
            )
            return {
                "name": _("Generated Attendances Selection"),
                "type": "ir.actions.act_window",
                "res_model": "hr_timesheet.sheet.generated.attendances.selection",
                "view_mode": "form",
                "view_id": form_view.id,
                "target": "new",
                "context": {"attendances": generated_attendances.ids},
            }

    def action_generate_attendances(self):
        # Check if the user has permission to generate attendances
        if self.env["hr.attendance"].check_access_rights(
            "create",
            raise_exception=False,
        ):
            return self.generate_attendances()

    def _generate_attendances_on_date(self, date):
        # Generate the attendances on a date respecting the
        # employee's calendar and established working hours
        self.ensure_one()
        calendar = self.employee_id.resource_calendar_id
        employee_time_zone = self._get_employee_timezone()
        generated_attendances = self.env["hr.attendance"]

        # Generate the attendances from the established working hours
        date_start = employee_time_zone.localize(
            datetime.combine(date, datetime.min.time())
        )
        date_end = employee_time_zone.localize(
            datetime.combine(date, datetime.max.time())
        )
        work_intervals = calendar._attendance_intervals_batch(date_start, date_end)
        if len(work_intervals) >= 1:
            work_intervals = work_intervals[0]

        for start, stop, _meta in work_intervals:
            check_in_time = start.astimezone(pytz.UTC).replace(tzinfo=None)
            check_out_time = stop.astimezone(pytz.UTC).replace(tzinfo=None)

            # Check if the attendance is out of the timesheet dates
            # (can happen due to timezone conversions)
            out_of_time_ranges = (
                check_in_time.date() < self.date_start
                or check_in_time.date() > self.date_end
                or check_out_time.date() < self.date_start
                or check_out_time.date() > self.date_end
            )
            # Check for possible overlapping attendances
            overlapping_attendances = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("check_in", "<=", check_out_time),
                    "|",
                    ("check_out", ">=", check_in_time),
                    ("check_out", "=", False),
                ]
            )

            # Create the attendances with the retrieved data
            if not (out_of_time_ranges or overlapping_attendances):
                generated_attendances |= self.env["hr.attendance"].create(
                    {
                        "employee_id": self.employee_id.id,
                        "check_in": check_in_time,
                        "check_out": check_out_time,
                        "sheet_id": self.id,
                    }
                )
        return generated_attendances

    def generate_attendances(self):
        # Check the dates that have imputed hours in the timesheet but no
        # attendances and generate those missing attendances
        for sheet in self:
            filtered_tsheets = sheet.timesheet_ids
            # Get the dates that have any hours imputed in the sheet
            # Remove lines generated from holidays or leaves (if any)
            if filtered_tsheets:
                line = filtered_tsheets[0]
                if hasattr(line, "holiday_id") and hasattr(line, "global_leave_id"):
                    filtered_tsheets = filtered_tsheets.filtered(
                        lambda r: not r.holiday_id and not r.global_leave_id
                    )

            timesheet_dates = set(filtered_tsheets.mapped("date"))
            generation_dates = set()
            created_attendances = self.env["hr.attendance"]
            # If a date has timesheet lines but not attendances,
            # attendances are generated using the employee's established working hours
            for date in sorted(timesheet_dates):
                if sheet._missing_attendances(date):
                    generation_dates.add(date)

            # The attendances are generated for that date
            for date in sorted(generation_dates):
                created_attendances |= sheet._generate_attendances_on_date(date)
            return created_attendances

    def _get_employee_timezone(self):
        # Get the sheet's employee (user) timezone
        self.ensure_one()
        tz = False
        if self.employee_id.user_id:
            tz = self.employee_id.user_id.partner_id.tz
        time_zone = pytz.timezone(tz or "UTC")
        return time_zone

    def _missing_attendances(self, date):
        # Check if date is included in any attendances
        # (there are imputed attendances in that date)
        self.ensure_one()
        for att in self.attendances_ids:
            start_date = att._get_attendance_employee_tz(att.check_in)
            end_date = att._get_attendance_employee_tz(att.check_out)
            if not end_date and start_date <= date:
                return False
            elif start_date <= date <= end_date:
                return False
        return True
