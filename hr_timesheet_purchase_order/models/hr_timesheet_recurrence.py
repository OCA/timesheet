# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from calendar import monthrange

from dateutil.relativedelta import relativedelta
from dateutil.rrule import (
    DAILY,
    FR,
    MO,
    MONTHLY,
    SA,
    SU,
    TH,
    TU,
    WE,
    WEEKLY,
    YEARLY,
    rrule,
)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

MONTHS = {
    "january": 31,
    "february": 28,
    "march": 31,
    "april": 30,
    "may": 31,
    "june": 30,
    "july": 31,
    "august": 31,
    "september": 30,
    "october": 31,
    "november": 30,
    "december": 31,
}

DAYS = {
    "mon": MO,
    "tue": TU,
    "wed": WE,
    "thu": TH,
    "fri": FR,
    "sat": SA,
    "sun": SU,
}

WEEKS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "last": 4,
}


class HRTimeSheetRecurrence(models.Model):
    _name = "hr.timesheet.recurrence"
    _description = "HR TimeSheet Recurrence"

    partner_ids = fields.One2many("res.partner", "recurrence_id")
    next_recurrence_date = fields.Date()
    recurrence_left = fields.Integer(string="Number of tasks left to create")

    repeat_interval = fields.Integer(string="Repeat Every", default=1)
    repeat_unit = fields.Selection(
        [
            ("day", "Days"),
            ("week", "Weeks"),
            ("month", "Months"),
            ("year", "Years"),
        ],
        default="week",
    )
    repeat_type = fields.Selection(
        [
            ("forever", "Forever"),
            ("until", "End Date"),
            ("after", "Number of Repetitions"),
        ],
        default="forever",
        string="Until",
    )
    repeat_until = fields.Date(string="End Date")
    repeat_number = fields.Integer(string="Repetitions")

    repeat_on_month = fields.Selection(
        [
            ("date", "Date of the Month"),
            ("day", "Day of the Month"),
        ]
    )

    repeat_on_year = fields.Selection(
        [
            ("date", "Date of the Year"),
            ("day", "Day of the Year"),
        ]
    )

    mon = fields.Boolean(string="Mon")
    tue = fields.Boolean(string="Tue")
    wed = fields.Boolean(string="Wed")
    thu = fields.Boolean(string="Thu")
    fri = fields.Boolean(string="Fri")
    sat = fields.Boolean(string="Sat")
    sun = fields.Boolean(string="Sun")

    repeat_day = fields.Integer()
    repeat_week = fields.Selection(
        [
            ("first", "First"),
            ("second", "Second"),
            ("third", "Third"),
            ("last", "Last"),
        ]
    )
    repeat_weekday = fields.Selection(
        [
            ("mon", "Monday"),
            ("tue", "Tuesday"),
            ("wed", "Wednesday"),
            ("thu", "Thursday"),
            ("fri", "Friday"),
            ("sat", "Saturday"),
            ("sun", "Sunday"),
        ],
        string="Day Of The Week",
        readonly=False,
    )
    repeat_month = fields.Selection(
        [
            ("january", "January"),
            ("february", "February"),
            ("march", "March"),
            ("april", "April"),
            ("may", "May"),
            ("june", "June"),
            ("july", "July"),
            ("august", "August"),
            ("september", "September"),
            ("october", "October"),
            ("november", "November"),
            ("december", "December"),
        ]
    )

    @api.constrains("repeat_unit", "mon", "tue", "wed", "thu", "fri", "sat", "sun")
    def _check_recurrence_days(self):
        for timesheet in self.filtered(lambda p: p.repeat_unit == "week"):
            if not any([getattr(timesheet, attr_name) for attr_name in DAYS]):
                raise ValidationError(_("You should select a least one day"))

    @api.constrains("repeat_interval")
    def _check_repeat_interval(self):
        if self.filtered(lambda t: t.repeat_interval <= 0):
            raise ValidationError(_("The interval should be greater than 0"))

    @api.constrains("repeat_number", "repeat_type")
    def _check_repeat_number(self):
        if self.filtered(lambda t: t.repeat_type == "after" and t.repeat_number <= 0):
            raise ValidationError(_("Should repeat at least once"))

    @api.constrains("repeat_type", "repeat_until")
    def _check_repeat_until_date(self):
        today = fields.Date.today()
        if self.filtered(lambda t: t.repeat_type == "until" and t.repeat_until < today):
            raise ValidationError(_("The end date should be in the future"))

    @api.constrains(
        "repeat_unit", "repeat_on_month", "repeat_day", "repeat_type", "repeat_until"
    )
    def _check_repeat_until_month(self):
        if self.filtered(
            lambda r: r.repeat_type == "until"
            and r.repeat_unit == "month"
            and r.repeat_until
            and r.repeat_on_month == "date"
            and int(r.repeat_day) > r.repeat_until.day
            and monthrange(r.repeat_until.year, r.repeat_until.month)[1]
            != r.repeat_until.day
        ):
            raise ValidationError(
                _(
                    "The end date should be after the day of "
                    "the month or the last day of the month"
                )
            )

    @api.constrains("repeat_day", "repeat_month")
    def _check_repeat_day_or_month(self):
        if 0 > self.repeat_day or self.repeat_day > 31:
            raise ValidationError(
                _(
                    "The number of days in a month cannot be negative "
                    "or more than 31 days"
                )
            )

    def _get_weekdays(self, n=1):
        self.ensure_one()
        if self.repeat_unit == "week":
            return [fn(n) for day, fn in DAYS.items() if self[day]]
        return [DAYS.get(self.repeat_weekday)(n)]

    @api.model
    def _get_next_recurring_dates(
        self,
        date_start,
        repeat_interval,
        repeat_unit,
        repeat_type,
        repeat_until,
        repeat_on_month,
        repeat_on_year,
        weekdays,
        repeat_day,
        repeat_week,
        repeat_month,
        **kwargs
    ):
        """Based on the selected parameters returns the following date"""

        count = kwargs.get("count", 1)
        rrule_kwargs = {"interval": repeat_interval or 1, "dtstart": date_start}
        repeat_day = int(repeat_day)
        if repeat_type == "until":
            rrule_kwargs["until"] = (
                repeat_until if repeat_until else fields.Date.today()
            )
        else:
            rrule_kwargs["count"] = count

        if (
            repeat_unit == "week"
            or (repeat_unit == "month" and repeat_on_month == "day")
            or (repeat_unit == "year" and repeat_on_year == "day")
        ):
            rrule_kwargs["byweekday"] = weekdays
        if repeat_unit == "day":
            rrule_kwargs["freq"] = DAILY
        elif repeat_unit == "month":
            rrule_kwargs["freq"] = MONTHLY
            if repeat_on_month == "date":
                return self._get_dates_for_next_recurrence(
                    date_start,
                    repeat_day,
                    repeat_interval,
                    repeat_until,
                    repeat_type,
                    count,
                )
        elif repeat_unit == "year":
            rrule_kwargs["freq"] = YEARLY
            month = list(MONTHS.keys()).index(repeat_month) + 1
            rrule_kwargs["bymonth"] = month
            if repeat_on_year == "date":
                rrule_kwargs["bymonthday"] = min(repeat_day, MONTHS.get(repeat_month))
                rrule_kwargs["bymonth"] = month
        else:
            rrule_kwargs["freq"] = WEEKLY
        rules = rrule(**rrule_kwargs)
        return list(rules) if rules else []

    def _get_dates_for_next_recurrence(
        self, date_start, repeat_day, repeat_interval, repeat_until, repeat_type, count
    ):
        dates = []
        start = date_start - relativedelta(days=1)
        start = start.replace(
            day=min(repeat_day, monthrange(start.year, start.month)[1])
        )
        if start < date_start:
            # Ensure the next recurrence is in the future
            start += relativedelta(months=repeat_interval)
            start = start.replace(
                day=min(repeat_day, monthrange(start.year, start.month)[1])
            )
        can_generate_date = (
            (lambda: start <= repeat_until)
            if repeat_type == "until"
            else (lambda: len(dates) < count)
        )
        while can_generate_date():
            dates.append(start)
            start += relativedelta(months=repeat_interval)
            start = start.replace(
                day=min(repeat_day, monthrange(start.year, start.month)[1])
            )
        return dates

    def _set_next_recurrence_date(self):
        today = fields.Date.today()
        tomorrow = today + relativedelta(days=1)
        for recurrence in self.filtered(
            lambda r: r.repeat_type == "after"
            and r.recurrence_left >= 0
            or r.repeat_type == "until"
            and r.repeat_until >= today
            or r.repeat_type == "forever"
        ):
            if recurrence.repeat_type == "after" and recurrence.recurrence_left == 0:
                recurrence.next_recurrence_date = False
            else:
                next_date = self._get_next_recurring_dates(
                    tomorrow,
                    recurrence.repeat_interval,
                    recurrence.repeat_unit,
                    recurrence.repeat_type,
                    recurrence.repeat_until,
                    recurrence.repeat_on_month,
                    recurrence.repeat_on_year,
                    recurrence._get_weekdays(),
                    recurrence.repeat_day,
                    recurrence.repeat_week,
                    recurrence.repeat_month,
                    count=1,
                )
                recurrence.next_recurrence_date = next_date[0] if next_date else False

    def _create_purchase_order(self):
        for partner in self.partner_ids:

            timesheets = partner.mapped("employee_ids.timesheet_sheet_ids").filtered(
                lambda t: not t.purchase_order_id and t.state == "done"
            )
            if not timesheets:
                continue
            timesheets.action_create_purchase_order()
            if partner.is_send_po:
                email_act = timesheets[0].purchase_order_id.action_rfq_send()
                email_ctx = email_act.get("context", {})
                timesheets[0].purchase_order_id.with_context(
                    **email_ctx
                ).message_post_with_template(email_ctx.get("default_template_id"))

    @api.model
    def _cron_generate_auto_po(self):
        """Generate purchase order for all partner with timesheets"""
        today = fields.Date.today()
        recurring_today = self.search([("next_recurrence_date", "<=", today)])
        recurring_today._create_purchase_order()
        for recurrence in recurring_today.filtered(lambda r: r.repeat_type == "after"):
            recurrence.recurrence_left -= 1
        recurring_today._set_next_recurrence_date()

    @api.model
    def create(self, vals):
        if vals.get("repeat_number"):
            vals["recurrence_left"] = vals.get("repeat_number")
        res = super().create(vals)
        res._set_next_recurrence_date()
        return res

    def write(self, vals):
        if vals.get("repeat_number"):
            vals["recurrence_left"] = vals.get("repeat_number")
        res = super().write(vals)
        if "next_recurrence_date" not in vals:
            self._set_next_recurrence_date()
        return res
