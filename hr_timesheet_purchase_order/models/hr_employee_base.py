from datetime import timedelta

from odoo import api, fields, models

from .hr_timesheet_recurrence import DAYS


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    allow_generate_purchase_order = fields.Boolean(string="Generate POs from Timesheet")
    billing_partner_id = fields.Many2one("res.partner")

    is_auto_po_generate = fields.Boolean(string="Automatic PO generation")
    recurrence_id = fields.Many2one("hr.timesheet.recurrence", copy=False)

    is_send_po = fields.Boolean(string="Send RFQ by email after creation")

    next_recurrence_date = fields.Date(related="recurrence_id.next_recurrence_date")
    repeat_interval = fields.Integer(
        string="Repeat Every", default=1, compute="_compute_repeat", readonly=False
    )
    repeat_unit = fields.Selection(
        [
            ("day", "Days"),
            ("week", "Weeks"),
            ("month", "Months"),
            ("year", "Years"),
        ],
        default="week",
        compute="_compute_repeat",
        readonly=False,
    )
    repeat_type = fields.Selection(
        [
            ("forever", "Forever"),
            ("until", "End Date"),
            ("after", "Number of Repetitions"),
        ],
        default="forever",
        string="Until",
        compute="_compute_repeat",
        readonly=False,
    )
    repeat_until = fields.Date(
        string="End Date", compute="_compute_repeat", readonly=False
    )
    repeat_number = fields.Integer(
        string="Repetitions", default=1, compute="_compute_repeat", readonly=False
    )

    repeat_on_month = fields.Selection(
        [
            ("date", "Date of the Month"),
            ("day", "Day of the Month"),
        ],
        default="date",
        compute="_compute_repeat",
        readonly=False,
    )

    repeat_on_year = fields.Selection(
        [
            ("date", "Date of the Year"),
            ("day", "Day of the Year"),
        ],
        default="date",
        compute="_compute_repeat",
        readonly=False,
    )

    mon = fields.Boolean(string="Mon", compute="_compute_repeat", readonly=False)
    tue = fields.Boolean(string="Tue", compute="_compute_repeat", readonly=False)
    wed = fields.Boolean(string="Wed", compute="_compute_repeat", readonly=False)
    thu = fields.Boolean(string="Thu", compute="_compute_repeat", readonly=False)
    fri = fields.Boolean(string="Fri", compute="_compute_repeat", readonly=False)
    sat = fields.Boolean(string="Sat", compute="_compute_repeat", readonly=False)
    sun = fields.Boolean(string="Sun", compute="_compute_repeat", readonly=False)

    repeat_day = fields.Integer(
        compute="_compute_repeat",
        readonly=False,
    )

    @api.onchange("repeat_day", "repeat_month")
    def _onchange_repeat_day(self):
        if 0 > self.repeat_day or self.repeat_day > 31:
            self.repeat_day = 1
        if self.repeat_month == "february" and self.repeat_day > 29:
            self.repeat_day = 28

    repeat_week = fields.Selection(
        [
            ("first", "First"),
            ("second", "Second"),
            ("third", "Third"),
            ("last", "Last"),
        ],
        default="first",
        compute="_compute_repeat",
        readonly=False,
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
        compute="_compute_repeat",
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
        ],
        compute="_compute_repeat",
        readonly=False,
    )

    repeat_show_dow = fields.Boolean(compute="_compute_repeat_visibility")
    repeat_show_day = fields.Boolean(compute="_compute_repeat_visibility")
    repeat_show_week = fields.Boolean(compute="_compute_repeat_visibility")
    repeat_show_month = fields.Boolean(compute="_compute_repeat_visibility")

    @api.depends(
        "is_auto_po_generate", "repeat_unit", "repeat_on_month", "repeat_on_year"
    )
    def _compute_repeat_visibility(self):
        """Based on the selected parameters sets
        the fields that should be visible to the user
        """
        for item in self:
            item.repeat_show_day = (
                item.is_auto_po_generate
                and (item.repeat_unit == "month" and item.repeat_on_month == "date")
                or (item.repeat_unit == "year" and item.repeat_on_year == "date")
            )
            item.repeat_show_week = (
                item.is_auto_po_generate
                and (item.repeat_unit == "month" and item.repeat_on_month == "day")
                or (item.repeat_unit == "year" and item.repeat_on_year == "day")
            )
            item.repeat_show_dow = (
                item.is_auto_po_generate and item.repeat_unit == "week"
            )
            item.repeat_show_month = (
                item.is_auto_po_generate and item.repeat_unit == "year"
            )

    @api.depends("is_auto_po_generate")
    def _compute_repeat(self):
        rec_fields = self._get_recurrence_fields()
        defaults = self.default_get(rec_fields)
        for employee in self:
            for f in rec_fields:
                if employee.recurrence_id:
                    employee[f] = employee.recurrence_id[f]
                else:
                    employee[f] = (
                        defaults.get(f) if employee.is_auto_po_generate else False
                    )

    @api.model
    def _get_recurrence_fields(self):
        return [
            "repeat_interval",
            "repeat_unit",
            "repeat_type",
            "repeat_until",
            "repeat_number",
            "repeat_on_month",
            "repeat_on_year",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "sat",
            "sun",
            "repeat_day",
            "repeat_week",
            "repeat_month",
            "repeat_weekday",
        ]

    @api.model
    def default_get(self, default_fields):
        vals = super().default_get(default_fields)
        days = list(DAYS.keys())
        week_start = fields.Datetime.today().weekday()
        if all(d in default_fields for d in days):
            vals[days[week_start]] = True
        if "repeat_day" in default_fields:
            vals["repeat_day"] = str(fields.Datetime.today().day)
        if "repeat_month" in default_fields:
            vals["repeat_month"] = self._fields.get("repeat_month").selection[
                fields.Datetime.today().month - 1
            ][0]
        if "repeat_until" in default_fields:
            vals["repeat_until"] = fields.Date.today() + timedelta(days=7)
        if "repeat_weekday" in default_fields:
            vals["repeat_weekday"] = self._fields.get("repeat_weekday").selection[
                week_start
            ][0]
        return vals

    def write(self, vals):
        rec_fields = vals.keys() & self._get_recurrence_fields()
        if "is_auto_po_generate" in vals and not vals.get("is_auto_po_generate"):
            self.recurrence_id.unlink()
        if rec_fields:
            rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
            for timesheet in self:
                if timesheet.recurrence_id:
                    timesheet.recurrence_id.write(rec_values)
                elif vals.get("is_auto_po_generate"):
                    rec_values["next_recurrence_date"] = fields.Datetime.today()
                    recurrence = self.env["hr.timesheet.recurrence"].create(rec_values)
                    timesheet.recurrence_id = recurrence.id
        return super().write(vals)

    @api.model
    def create(self, vals):
        rec_fields = vals.keys() & self._get_recurrence_fields()
        if rec_fields and vals.get("is_auto_po_generate"):
            rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
            rec_values["next_recurrence_date"] = fields.Datetime.today()
            recurrence = self.env["hr.timesheet.recurrence"].create(rec_values)
            vals["recurrence_id"] = recurrence.id
        return super().create(vals)
