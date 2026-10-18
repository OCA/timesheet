# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    time_begin = fields.Float(
        compute="_compute_time_begin", inverse="_inverse_time_begin", string="Begin"
    )
    time_end = fields.Float(
        compute="_compute_time_end", inverse="_inverse_time_end", string="End"
    )

    @api.depends("date_time")
    def _compute_time_begin(self):
        for record in self:
            if record.date_time:
                tz = (
                    pytz.timezone(record.employee_id.tz)
                    if record.employee_id.tz
                    else pytz.timezone(self.env.user.tz or "UTC")
                )
                date = record.date_time.astimezone(tz)
                record.time_begin = date.hour + (date.minute / 60.0)
            else:
                record.time_begin = False

    @api.depends("date_time_end")
    def _compute_time_end(self):
        for record in self:
            if record.date_time_end:
                tz = (
                    pytz.timezone(record.employee_id.tz)
                    if record.employee_id.tz
                    else pytz.timezone(self.env.user.tz or "UTC")
                )
                date = record.date_time_end.astimezone(tz)
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
            return pytz.utc.localize(self.date_time).astimezone(tz).date()
        return False

    def _local_to_utc(self, tz, day, hours, minutes):
        local = tz.localize(datetime.combine(day, time(hours, minutes)))
        return local.astimezone(pytz.utc).replace(tzinfo=None)

    def _inverse_time_begin(self):
        for record in self:
            tz = (
                pytz.timezone(record.employee_id.tz)
                if record.employee_id.tz
                else pytz.timezone(self.env.user.tz or "UTC")
            )
            day = record._get_local_day(tz)
            if not day:
                continue
            hours = int(record.time_begin)
            minutes = int(round((record.time_begin - hours) * 60))
            record.date_time = record._local_to_utc(tz, day, hours, minutes)

    def _inverse_time_end(self):
        for record in self:
            if record.time_end <= 0:
                record.date_time_end = False
                record.time_end = 0
                record.unit_amount = 0
                continue

            tz = (
                pytz.timezone(record.employee_id.tz)
                if record.employee_id.tz
                else pytz.timezone(self.env.user.tz or "UTC")
            )
            day = record._get_local_day(tz)
            if not day:
                continue

            hours = int(record.time_end)
            minutes = int(round((record.time_end - hours) * 60))
            date_time_end = record._local_to_utc(tz, day, hours % 24, minutes)
            day_offset = hours // 24
            if day_offset > 0:
                date_time_end += relativedelta(days=day_offset)
            if record.date_time and date_time_end < record.date_time:
                date_time_end += relativedelta(days=1)

            record.date_time_end = date_time_end

            if record.time_end >= 24:
                record.time_end = record.time_end % 24

    @api.onchange("time_begin")
    def _onchange_time_begin(self):
        self._inverse_time_begin()

    @api.onchange("time_end")
    def _onchange_time_end(self):
        self._inverse_time_end()

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
                ctx["default_date"] = default_date_time.date()
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
