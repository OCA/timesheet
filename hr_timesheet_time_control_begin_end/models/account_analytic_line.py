# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    # Both fields share one inverse: the ORM only puts the values of the
    # inverse being run in cache, so separate inverses could not see each
    # other and would depend on the order of the fields in vals.
    time_begin = fields.Float(
        compute="_compute_time_begin",
        inverse="_inverse_time_begin_end",
        string="Begin",
    )
    time_end = fields.Float(
        compute="_compute_time_end",
        inverse="_inverse_time_begin_end",
        string="End",
    )

    def _get_tz(self):
        self.ensure_one()
        return pytz.timezone(self.employee_id.tz or self.env.user.tz or "UTC")

    @api.model
    def _to_local(self, datetime_, tz):
        return pytz.utc.localize(datetime_).astimezone(tz)

    @api.model
    def _local_to_utc(self, tz, day, hours, minutes):
        local = tz.localize(datetime.combine(day, time(hours, minutes)))
        return local.astimezone(pytz.utc).replace(tzinfo=None)

    @api.model
    def _float_to_hours_minutes(self, value):
        hours = int(value)
        minutes = int(round((value - hours) * 60))
        if minutes == 60:
            hours, minutes = hours + 1, 0
        return hours, minutes

    @api.model
    def _eval_date(self, vals):
        # Derive ``date`` from ``date_time`` in the employee's timezone, the
        # same timezone time_begin/time_end are expressed in.
        if vals.get("employee_id"):
            employee = self.env["hr.employee"].browse(vals["employee_id"])
        else:
            employee = self.employee_id
        line = self
        if len(employee) == 1 and employee.tz:
            line = self.with_context(tz=employee.tz)
        return super(AccountAnalyticLine, line)._eval_date(vals)

    @api.depends("date_time")
    def _compute_time_begin(self):
        for record in self:
            if record.date_time:
                date = self._to_local(record.date_time, record._get_tz())
                record.time_begin = date.hour + (date.minute / 60.0)
            else:
                record.time_begin = False

    @api.depends("date_time_end")
    def _compute_time_end(self):
        for record in self:
            if record.date_time_end:
                date = self._to_local(record.date_time_end, record._get_tz())
                record.time_end = date.hour + (date.minute / 60.0)
            else:
                record.time_end = False

    def _get_local_day(self, tz):
        """Day the line belongs to, in the employee's timezone.

        ``date`` is the authoritative day. ``date_time`` may have been filled
        with ``date`` + the current UTC time, which can fall on another day
        once converted to the employee's timezone.
        """
        self.ensure_one()
        if self.date:
            return self.date
        if self.date_time:
            return self._to_local(self.date_time, tz).date()
        return False

    def _apply_time_begin(self):
        """Set ``date_time`` from ``date`` and ``time_begin``."""
        for record in self:
            tz = record._get_tz()
            day = record._get_local_day(tz)
            if not day:
                continue
            hours, minutes = self._float_to_hours_minutes(record.time_begin)
            record.date_time = self._local_to_utc(tz, day, hours, minutes)

    def _apply_time_end(self):
        """Set ``date_time_end`` from ``date`` and ``time_end``."""
        for record in self:
            if record.time_end <= 0:
                record.date_time_end = False
                record.time_end = 0
                record.unit_amount = 0
                continue

            tz = record._get_tz()
            day = record._get_local_day(tz)
            if not day:
                continue

            hours, minutes = self._float_to_hours_minutes(record.time_end)
            date_time_end = self._local_to_utc(tz, day, hours % 24, minutes)
            day_offset = hours // 24
            if day_offset > 0:
                date_time_end += relativedelta(days=day_offset)
            if record.date_time and date_time_end < record.date_time:
                date_time_end += relativedelta(days=1)

            record.date_time_end = date_time_end

            if record.time_end >= 24:
                record.time_end = record.time_end % 24

    def _inverse_time_begin_end(self):
        # Fields being written are protected from recomputation; use that to
        # only apply what was actually written. time_begin goes first, as
        # date_time_end is recomputed from date_time and unit_amount.
        begin_field = self._fields["time_begin"]
        end_field = self._fields["time_end"]
        for record in self:
            write_begin = self.env.is_protected(begin_field, record)
            write_end = self.env.is_protected(end_field, record)
            if not (write_begin or write_end):
                write_begin = write_end = True
            if write_begin:
                record._apply_time_begin()
            if write_end:
                record._apply_time_end()

    @api.onchange("time_begin")
    def _onchange_time_begin(self):
        self._apply_time_begin()

    @api.onchange("time_end")
    def _onchange_time_end(self):
        self._apply_time_end()

    @api.onchange("date")
    def _onchange_date(self):
        # Keep the local time of day when moving the line to another day.
        hour_uom = self.env.ref("uom.product_uom_hour")
        if self.product_uom_id == hour_uom and self.date_time and self.date:
            self.date_time = self._move_to_day(self.date_time, self.date)

    @api.onchange("date_time", "date_time_end")
    def _onchange_date_time(self):
        res = super()._onchange_date_time()
        if self.date_time:
            self.date = self._to_local(self.date_time, self._get_tz()).date()
        return res

    def _move_to_day(self, datetime_, day):
        """Return ``datetime_`` moved to ``day``, keeping the local time."""
        self.ensure_one()
        tz = self._get_tz()
        local = self._to_local(datetime_, tz)
        moved = tz.localize(datetime.combine(day, local.time()))
        return moved.astimezone(pytz.utc).replace(tzinfo=None)

    def write(self, vals):
        # project_timesheet_time_control combines the new date with the UTC
        # time of date_time, which shifts the day east of UTC.
        if "date" in vals and "date_time" not in vals:
            day = fields.Date.to_date(vals["date"])
            with_date_time = self.filtered("date_time")
            for record in with_date_time:
                super(AccountAnalyticLine, record).write(
                    dict(vals, date_time=record._move_to_day(record.date_time, day))
                )
            return super(AccountAnalyticLine, self - with_date_time).write(vals)
        return super().write(vals)

    @api.model
    def default_get(self, fields_list):
        ctx = self.env.context
        if self.env.context.get("default_date_time") and not self.env.context.get(
            "default_date"
        ):
            ctx = dict(self.env.context)
            if default_date_time := self.env.context.get("default_date_time"):
                if isinstance(default_date_time, str):
                    default_date_time = fields.Datetime.from_string(default_date_time)
                ctx["default_date"] = fields.Date.context_today(self, default_date_time)
        vals = super(AccountAnalyticLine, self.with_context(**ctx)).default_get(
            list(fields_list) + ["product_uom_id"]
        )
        if (
            vals.get("date_time")
            and vals.get("date_time_end")
            and vals.get("product_uom_id") == self.env.ref("uom.product_uom_hour").id
        ):
            vals["unit_amount"] = (
                vals.get("date_time_end") - vals.get("date_time")
            ).total_seconds() / 3600
        if "product_uom_id" not in fields_list and "product_uom_id" in vals:
            del vals["product_uom_id"]
        return vals
