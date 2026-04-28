from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def _get_default_start_time(self):
        # Set the default start time according to setting to now
        # or after the previous entry.
        params = self.env["ir.config_parameter"].sudo()
        timesheet_alignment = params.get_param(
            "hr_timesheet_time_control.timesheet_alignment"
        )
        # default to now
        start_time = super()._get_default_start_time()
        if timesheet_alignment == "now":
            return start_time
        defaults = self.default_get(["employee_id", "company_id", "date"])
        date_day = defaults.get("date", start_time.date())
        start_time = datetime.combine(
            date_day,
            time(hour=start_time.hour, minute=start_time.minute, second=0),
        )
        employee_id = defaults.get(
            "employee_id",
            self.env.user.employee_id.id,
        )
        if not employee_id:
            return start_time
        # get the last entry of the employee on the same day
        # (searching for date_time_end would be better, but is not working)
        analytic_lines = self.env[self._name].search(
            [
                ["employee_id", "=", employee_id],
                ["date", "=", date_day],
                ["date_time", "!=", False],
            ],
            order="date_time desc",
            limit=1,
        )
        if analytic_lines.date_time_end:
            start_time = analytic_lines.date_time_end
        elif not analytic_lines:
            # if employee has no analytic_lines at this day,
            # get the employee calendar and set the start time
            # to the first interval of the day
            employee = self.env["hr.employee"].browse(employee_id)
            if employee.resource_calendar_id:
                start_date = datetime.combine(
                    date_day, time(0, tzinfo=pytz.timezone(employee.tz))
                )
                end_date = start_date + timedelta(days=1)
                intervals = employee.resource_calendar_id._work_intervals_batch(
                    start_date, end_date
                ).get(False, False)
                if intervals and intervals._items:
                    start_time = (
                        intervals._items[0][0].astimezone(pytz.UTC).replace(tzinfo=None)
                    )
        return start_time

    @api.model
    def _eval_date(self, vals):
        ctx = {}
        if vals.get("employee_id"):
            ctx["default_employee_id"] = vals["employee_id"]
        # Should be replaced by something like this:
        return super(AccountAnalyticLine, self.with_context(**ctx))._eval_date(vals)

    def _add_missing_default_values(self, vals):
        if "employee_id" in vals:
            self = self.with_context(default_employee_id=vals["employee_id"])
        if "date" in vals:
            self = self.with_context(default_date=vals["date"])
        elif "date_time" in vals:
            self = self.with_context(default_date=vals["date_time"].date())
        elif "date_time_end" in vals:
            self = self.with_context(default_date=vals["date_time_end"].date())
        return super()._add_missing_default_values(vals)

    @api.onchange("product_uom_id", "date_time", "date_time_end")
    def _compute_unit_amount(self):
        hour_uom = self.env.ref("uom.product_uom_hour")
        for record in self:
            if (
                record.product_uom_id == hour_uom
                and record.date_time_end
                and record.date_time
            ):
                # When date_time_end or date_time is not set, the unit_amount is updated
                record.unit_amount = (
                    record.date_time_end - record.date_time
                ).total_seconds() / 3600

    @api.model
    def default_get(self, fields_list):
        # Convert default_date_time from string to datetime
        default_date_time = self.env.context.get("default_date_time")
        default_date_time_end = self.env.context.get("default_date_time_end")
        if isinstance(default_date_time, str):
            default_date_time = fields.Datetime.from_string(default_date_time)
        if isinstance(default_date_time_end, str):
            default_date_time_end = fields.Datetime.from_string(default_date_time_end)
        ctx = {}
        if default_date_time:
            ctx["default_date_time"] = default_date_time
        if default_date_time_end:
            ctx["default_date_time_end"] = default_date_time_end
        vals = super(
            AccountAnalyticLine,
            self.with_context(**ctx),
        ).default_get(fields_list)
        # Handle calendar context: fill in date_time_end and unit_amount
        # when calendar creates a quick event with a time range
        if "date_time_end" in fields_list:
            if default_date_time_end:
                vals["date_time_end"] = default_date_time_end

        # Calculate unit_amount if both start and end times are available
        date_time = vals.get("date_time") or default_date_time
        if "unit_amount" in fields_list:
            date_time_end = vals.get("date_time_end") or default_date_time_end
            if date_time and date_time_end:
                # Calculate duration in hours
                duration = date_time_end - date_time
                hours = duration.total_seconds() / 3600
                vals["unit_amount"] = max(0, hours)
        if date_time:
            vals["date"] = date_time.date()
        if (
            self.env.context.get("is_timesheet", False)
            and "product_uom_id" in fields_list
            and "product_uom_id" not in vals
        ):
            company_id = vals.get("company_id")
            company = False
            if company_id:
                company = self.env["res.company"].browse(company_id)
            if not company:
                employee_in_id = vals.get(
                    "employee_id", self.env.context.get("default_employee_id", False)
                )
                if employee_in_id:
                    company = self.env["hr.employee"].browse(employee_in_id).company_id
                else:
                    company = self.env["res.company"].browse(self.env.company.id)
            if "company_id" in fields_list:
                vals["company_id"] = company.id
            if company:
                vals["product_uom_id"] = company.project_time_mode_id.id
        return vals

    @api.model
    def duplicate_today(self, record_id):
        record = self.browse(record_id)
        date_today = fields.Datetime.now(self.env.user.partner_id.tz).date()
        date_time_today = datetime.combine(date_today, record.date_time.time())
        date_time_end_today = datetime.combine(
            date_today,
            record.date_time_end.time()
            if record.date_time_end
            else date_time_today.time(),
        )
        defaults = {
            "date": date_today,
            "date_time": date_time_today,
            "date_time_end": date_time_end_today,
        }
        new_record = record.copy(defaults)
        return new_record.id
