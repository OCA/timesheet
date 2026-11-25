# Copyright 2026 glueckkanja AG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, time

import pytz

from odoo import models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _generate_timesheets(self, ignored_resource_calendar_leaves=None):
        # The start time lookup has to ignore the same resource leaves the
        # generation ignores, or a day would look free of working hours.
        return super(
            HrLeave,
            self.with_context(
                holiday_timesheet_ignored_calendar_leaves=list(
                    ignored_resource_calendar_leaves or []
                )
            ),
        )._generate_timesheets(
            ignored_resource_calendar_leaves=ignored_resource_calendar_leaves
        )

    def _timesheet_prepare_line_values(
        self, index, work_hours_data, day_date, work_hours_count, project, task
    ):
        vals = super()._timesheet_prepare_line_values(
            index, work_hours_data, day_date, work_hours_count, project, task
        )
        start = self._timesheet_work_start(day_date)
        if start:
            vals["date_time"] = start
        return vals

    def _timesheet_working_hours_calendar(self):
        """The calendar whose attendances give the entries their start.

        Same fallback chain as ``_list_work_time_per_day`` uses for the hours.
        """
        self.ensure_one()
        return (
            self.resource_calendar_id
            or self.employee_id.resource_calendar_id
            or self.employee_id.company_id.resource_calendar_id
        )

    def _timesheet_work_start(self, day):
        """When the employee starts working on that day of the leave.

        The first of the work intervals ``_generate_timesheets`` sums up into
        the hours of the day, as a naive UTC datetime. A flexible calendar has
        no attendances and gives nothing, so does a day without work.
        """
        self.ensure_one()
        calendar = self._timesheet_working_hours_calendar()
        resource = self.employee_id.resource_id
        if (
            not calendar
            or calendar.flexible_hours
            or not resource
            or not self.date_from
            or not self.date_to
        ):
            return None
        # The days are split in the tz of the resource, like the hours are.
        tz = pytz.timezone(resource.tz or calendar.tz)
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
        # The resource leave of the request itself would make the day free.
        ignored = list(
            self.env.context.get("holiday_timesheet_ignored_calendar_leaves") or []
        )
        ignored += (
            self.env["resource.calendar.leaves"]
            .sudo()
            .search([("holiday_id", "=", self.id)])
            .ids
        )
        intervals = calendar._work_intervals_batch(
            start_dt,
            end_dt,
            resource,
            [("id", "not in", ignored)] if ignored else None,
        )[resource.id]
        for start, _stop, _meta in intervals:
            return start.astimezone(pytz.utc).replace(tzinfo=None)
        return None
