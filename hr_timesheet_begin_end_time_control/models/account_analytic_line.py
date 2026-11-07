# Copyright 2026 OBS Solutions B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models

TIMER_FIELDS = {"date_time", "unit_amount"}
BEGIN_END_FIELDS = {"time_start", "time_stop"}


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    # --- helpers ---

    def _get_begin_end_tz(self):
        """Time zone in which begin and end hours are expressed."""
        self.ensure_one()
        return pytz.timezone(self.employee_id.tz or self.env.user.tz or "UTC")

    def _get_begin_end_unworked_hours(self, vals=None):
        """Hours between begin and end that are not worked.

        The end hour is start + duration + this value. Supports the break of
        ``hr_timesheet_begin_end_break`` (taken from ``vals`` when it is being
        written); other modules can extend it.
        """
        self.ensure_one()
        if vals and "break_duration" in vals:
            return vals["break_duration"] or 0.0
        return "break_duration" in self._fields and self["break_duration"] or 0.0

    @staticmethod
    def _float_hour(value):
        return value.hour + value.minute / 60 + value.second / 3600

    def _compute_begin_end_from_timer(self, date_time, unit_amount, vals=None):
        """Begin/end hours for a timer start and duration.

        :return: ``(time_start, time_stop)`` or ``None`` when they cannot be
            expressed on a single day.
        """
        self.ensure_one()
        if not date_time or not unit_amount or unit_amount < 0:
            return None
        date_time = fields.Datetime.to_datetime(date_time)
        tz = self._get_begin_end_tz()
        start = pytz.utc.localize(date_time).astimezone(tz)
        end = start + timedelta(
            hours=unit_amount + self._get_begin_end_unworked_hours(vals)
        )
        if end.date() != start.date():
            return None
        return self._float_hour(start), self._float_hour(end)

    def _compute_timer_start_from_begin(self, line_date, time_start):
        """UTC start datetime for a begin hour on the line's date."""
        self.ensure_one()
        tz = self._get_begin_end_tz()
        local = datetime.combine(fields.Date.to_date(line_date), time()) + timedelta(
            hours=time_start
        )
        return tz.localize(local).astimezone(pytz.utc).replace(tzinfo=None)

    def _begin_end_overlaps(self, line_date, time_start, time_stop):
        """Mirror of the overlap check of hr_timesheet_begin_end."""
        self.ensure_one()
        return bool(
            self.search_count(
                [
                    ("id", "!=", self.id),
                    ("employee_id", "=", self.employee_id.id),
                    ("date", "=", line_date),
                    ("time_start", "<", time_stop),
                    ("time_stop", ">", time_start),
                ],
                limit=1,
            )
        )

    def _prepare_begin_end_vals(self, date_time, unit_amount, line_date, vals=None):
        """Begin/end values following the timer, or empty hours."""
        self.ensure_one()
        hours = self._compute_begin_end_from_timer(date_time, unit_amount, vals)
        if hours and not self._begin_end_overlaps(line_date, *hours):
            return {"time_start": hours[0], "time_stop": hours[1]}
        return {"time_start": 0.0, "time_stop": 0.0}

    # --- CRUD ---

    @api.model_create_multi
    def create(self, vals_list):
        """A line entered with begin/end hours gets its timer start aligned.

        The other direction is left out on purpose: ``date_time`` defaults to
        now, so a line created with only a duration would get made-up hours.
        Timers fill begin/end when they stop (a write).
        """
        lines = super().create(vals_list)
        for line, vals in zip(lines, vals_list, strict=True):
            if (
                BEGIN_END_FIELDS & vals.keys()
                and "date_time" not in vals
                and line.time_start
            ):
                line.with_context(
                    begin_end_sync=True
                ).date_time = line._compute_timer_start_from_begin(
                    line.date, line.time_start
                )
        return lines

    def write(self, vals):
        if self.env.context.get("begin_end_sync"):
            return super().write(vals)
        if BEGIN_END_FIELDS & vals.keys():
            if "date_time" in vals:
                return super().write(vals)
            prepare = "_prepare_begin_end_to_timer_vals"
        elif TIMER_FIELDS & vals.keys():
            prepare = "_prepare_timer_to_begin_end_vals"
        else:
            return super().write(vals)
        # Per line, so each line's begin/end and timer are written together
        # and the duration constraint of hr_timesheet_begin_end sees
        # consistent values.
        res = True
        for line in self:
            res &= super(AccountAnalyticLine, line).write(getattr(line, prepare)(vals))
        return res

    def _prepare_begin_end_to_timer_vals(self, vals):
        """Begin hour edited: move the timer start along."""
        self.ensure_one()
        line_vals = dict(vals)
        time_start = vals.get("time_start", self.time_start)
        line_date = vals.get("date", self.date)
        if time_start and line_date:
            line_vals["date_time"] = self._compute_timer_start_from_begin(
                line_date, time_start
            )
        return line_vals

    def _prepare_timer_to_begin_end_vals(self, vals):
        """Timer start or duration changed: move begin/end along."""
        self.ensure_one()
        line_vals = dict(vals)
        unit_amount = vals.get("unit_amount", self.unit_amount)
        date_time = vals.get("date_time", self.date_time)
        # A running timer (start, no duration, no hours) being stopped, or
        # hours that were derived from the timer before this change.
        running_timer = bool(
            self.date_time
            and not self.unit_amount
            and not (self.time_start or self.time_stop)
        )
        if running_timer or self._is_begin_end_following_timer():
            line_date = (
                self._convert_datetime_to_date(date_time)
                if "date_time" in vals
                else vals.get("date", self.date)
            )
            line_vals.update(
                self._prepare_begin_end_vals(date_time, unit_amount, line_date, vals)
            )
        return line_vals

    def _is_begin_end_following_timer(self):
        """True when the current begin/end hours were derived from the timer."""
        self.ensure_one()
        if not (self.time_start or self.time_stop):
            return False
        hours = self._compute_begin_end_from_timer(self.date_time, self.unit_amount)
        # Begin/end hours are stored as floats; compare to the second.
        return bool(
            hours
            and abs(hours[0] - self.time_start) < 1 / 3600
            and abs(hours[1] - self.time_stop) < 1 / 3600
        )
