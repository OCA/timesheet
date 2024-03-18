# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from calendar import monthrange

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, rrule

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .consts import (
    DAYS,
    DAYS_IN_MONTHS,
    MONTH_SELECTION,
    ON_MONTH_SELECTION,
    ON_YEAR_SELECTION,
    TYPE_SELECTION,
    UNIT_SELECTION,
    WEEKDAY_SELECTION,
    WEEKS_SELECTION,
)


class HRTimeSheetRecurrence(models.Model):
    _name = "hr.timesheet.recurrence"
    _description = "HR TimeSheet Recurrence"

    partner_ids = fields.One2many("res.partner", "recurrence_id")
    next_recurrence_date = fields.Date()
    recurrence_left = fields.Integer(string="Number of tasks left to create")

    repeat_interval = fields.Integer(string="Repeat Every", default=1)
    repeat_unit = fields.Selection(
        selection=UNIT_SELECTION,
        default="week",
    )
    repeat_type = fields.Selection(
        selection=TYPE_SELECTION,
        default="forever",
        string="Until",
    )
    repeat_until = fields.Date(string="End Date")
    repeat_number = fields.Integer(string="Repetitions")

    repeat_on_month = fields.Selection(selection=ON_MONTH_SELECTION)

    repeat_on_year = fields.Selection(
        selection=ON_YEAR_SELECTION,
    )

    mon = fields.Boolean(string="Mon")
    tue = fields.Boolean(string="Tue")
    wed = fields.Boolean(string="Wed")
    thu = fields.Boolean(string="Thu")
    fri = fields.Boolean(string="Fri")
    sat = fields.Boolean(string="Sat")
    sun = fields.Boolean(string="Sun")

    repeat_day = fields.Integer()
    repeat_week = fields.Selection(selection=WEEKS_SELECTION)
    repeat_weekday = fields.Selection(
        selection=WEEKDAY_SELECTION,
        string="Day Of The Week",
        readonly=False,
    )
    repeat_month = fields.Selection(selection=MONTH_SELECTION)

    @api.constrains("repeat_unit", "mon", "tue", "wed", "thu", "fri", "sat", "sun")
    def _check_recurrence_days(self):
        """Check at least one day is selected for the recurrence"""
        for timesheet in self.filtered(lambda p: p.repeat_unit == "week"):
            if not any([getattr(timesheet, attr_name) for attr_name in DAYS]):
                raise ValidationError(_("You should select a least one day"))

    @api.constrains("repeat_interval")
    def _check_repeat_interval(self):
        """Check the interval is greater than 0"""
        if self.filtered(lambda t: t.repeat_interval <= 0):
            raise ValidationError(_("The interval should be greater than 0"))

    @api.constrains("repeat_number", "repeat_type")
    def _check_repeat_number(self):
        """Check the number of repetitions is greater than 0"""
        if self.filtered(lambda t: t.repeat_type == "after" and t.repeat_number <= 0):
            raise ValidationError(_("Should repeat at least once"))

    @api.constrains("repeat_type", "repeat_until")
    def _check_repeat_until_date(self):
        """Check the end date is in the future"""
        today = fields.Date.today()
        if self.filtered(lambda t: t.repeat_type == "until" and t.repeat_until < today):
            raise ValidationError(_("The end date should be in the future"))

    @api.constrains(
        "repeat_unit", "repeat_on_month", "repeat_day", "repeat_type", "repeat_until"
    )
    def _check_repeat_until_month(self):
        """Check the end date is after the day of the month or the last day of the month"""
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
        """Check the repeat day or month is valid"""
        month_day = DAYS_IN_MONTHS.get(self.repeat_month)
        if 0 > self.repeat_day or self.repeat_day > month_day:
            raise ValidationError(
                _(
                    (
                        "The number of days in a month cannot be negative "
                        "or more than %s days"
                    )
                    % self.repeat_day
                    if self.repeat_day < 0
                    else month_day
                )
            )

    def _get_weekdays(self, n=1):
        """Returns the weekdays selected for the recurrence
        Args:
            n (int, optional): Day of the week. Defaults to 1.
        Returns:
            list: The weekdays selected for the recurrence
        """
        self.ensure_one()
        if self.repeat_unit == "week":
            return [fn(n) for day, fn in DAYS.items() if self[day]]
        return [DAYS.get(self.repeat_weekday)(n)]

    @api.model
    def _get_next_recurring_dates(self, date_start, **recurrence_data):
        """Based on the selected parameters returns the following date

        Args:
            date_start (datetime): The starting date for calculating the recurring dates
            recurrence_data (dict): The recurrence pattern for calculating the dates

        Returns:
            datetime: The following date based on the selected parameters
        """

        count = recurrence_data.get("count", 1)

        rrule_kwargs = {
            "interval": recurrence_data.get("repeat_interval", 1),
            "dtstart": date_start,
        }
        repeat_day = int(recurrence_data.get("repeat_day", 0))
        repeat_type = recurrence_data.get("repeat_type", False)
        repeat_until = recurrence_data.get("repeat_until", False)
        if repeat_type == "until":
            rrule_kwargs["until"] = (
                repeat_until if repeat_until else fields.Date.today()
            )
        else:
            rrule_kwargs["count"] = count
        repeat_unit = recurrence_data.get("repeat_unit", False)
        repeat_on_month = recurrence_data.get("repeat_on_month", False)
        repeat_on_year = recurrence_data.get("repeat_on_year", False)
        repeat_month = recurrence_data.get("repeat_month", False)
        if (
            repeat_unit == "week"
            or (repeat_unit == "month" and repeat_on_month == "day")
            or (repeat_unit == "year" and repeat_on_year == "day")
        ):
            rrule_kwargs["byweekday"] = recurrence_data.get("weekdays", [])
        if repeat_unit == "day":
            rrule_kwargs["freq"] = DAILY
        elif repeat_unit == "month":
            rrule_kwargs["freq"] = MONTHLY
            if repeat_on_month == "date":
                return self._get_dates_for_next_recurrence(
                    date_start,
                    repeat_day,
                    count,
                    repeat_interval=recurrence_data.get("repeat_interval", False),
                    repeat_until=repeat_until,
                    repeat_type=repeat_type,
                )
        elif repeat_unit == "year":
            rrule_kwargs["freq"] = YEARLY
            month = list(DAYS_IN_MONTHS.keys()).index(repeat_month) + 1
            rrule_kwargs["bymonth"] = month
            if repeat_on_year == "date":
                rrule_kwargs["bymonthday"] = min(
                    repeat_day, DAYS_IN_MONTHS.get(repeat_month)
                )
                rrule_kwargs["bymonth"] = month
        else:
            rrule_kwargs["freq"] = WEEKLY
        rules = rrule(**rrule_kwargs)
        return list(rules) if rules else []

    def _get_dates_for_next_recurrence(
        self, date_start, repeat_day, count, **recurrence
    ):
        """Based on the selected parameters returns the following date

        Args:
            date_start (datetime): The starting date for calculating the recurring dates
            repeat_day (int): Repeat day count
            count (int): Count repeat dates
            recurrence (dict): The recurrence pattern for calculating the dates

        Returns:
            list: Dates list
        """
        dates = []
        start = date_start - relativedelta(days=1)
        start = start.replace(
            day=min(repeat_day, monthrange(start.year, start.month)[1])
        )
        repeat_interval = recurrence.get("repeat_interval", 0)
        repeat_until = recurrence.get("repeat_until", False)
        repeat_type = recurrence.get("repeat_type", False)
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
        """Set the next recurrence date"""
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
                    repeat_interval=recurrence.repeat_interval,
                    repeat_unit=recurrence.repeat_unit,
                    repeat_type=recurrence.repeat_type,
                    repeat_until=recurrence.repeat_until,
                    repeat_on_month=recurrence.repeat_on_month,
                    repeat_on_year=recurrence.repeat_on_year,
                    weekdays=recurrence._get_weekdays(),
                    repeat_day=recurrence.repeat_day,
                    repeat_week=recurrence.repeat_week,
                    repeat_month=recurrence.repeat_month,
                    count=1,
                )
                recurrence.next_recurrence_date = next_date[0] if next_date else False

    def _create_purchase_order(self):
        """Create purchase order for all timesheets of the partner"""
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
