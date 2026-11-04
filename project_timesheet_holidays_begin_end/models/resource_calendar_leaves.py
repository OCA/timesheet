# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, time

import pytz

from odoo import models


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    def _timesheet_prepare_line_values(
        self, index, employee_id, work_hours_data, day_date, work_hours_count
    ):
        vals = super()._timesheet_prepare_line_values(
            index, employee_id, work_hours_data, day_date, work_hours_count
        )
        start = self._timesheet_work_start(employee_id, day_date)
        if start:
            vals["date_time"] = start
        return vals

    def _timesheet_work_start(self, employee, day):
        """When the employee starts working on that day of the global time off.

        The first of the attendances ``_work_time_per_day`` sums up into the
        hours of the day, read in the tz of the calendar so it carries the
        real time of day, as a naive UTC datetime. A flexible calendar has no
        attendances and gives nothing, so does a day without work.
        """
        self.ensure_one()
        calendar = self.calendar_id or employee.resource_calendar_id
        if not calendar or calendar.flexible_hours or not self.date_from:
            return None
        tz = pytz.timezone(calendar.tz)
        start_dt = max(
            tz.localize(datetime.combine(day, time.min)),
            pytz.utc.localize(self.date_from),
        )
        end_dt = min(
            tz.localize(datetime.combine(day, time.max)),
            pytz.utc.localize(self.date_to),
        )
        if start_dt >= end_dt:
            return None
        intervals = calendar._attendance_intervals_batch(
            start_dt, end_dt, self.resource_id, tz=tz
        )[self.resource_id.id]
        for start, _stop, _meta in intervals:
            return start.astimezone(pytz.utc).replace(tzinfo=None)
        return None
