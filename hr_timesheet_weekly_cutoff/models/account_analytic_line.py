from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_outside_weekly_cutoff = fields.Boolean(
        string="Outside Weekly Cutoff",
        readonly=True,
        copy=False,
        index=True,
    )

    def _get_allowed_from_date(self):
        self.ensure_one()
        company = self.company_id
        today = fields.Date.context_today(self)
        lock_weekday = int(company.timesheet_lock_weekday or 0)
        current_weekday = today.weekday()
        days_since_lock = (current_weekday - lock_weekday) % 7
        lock_date = today - timedelta(days=days_since_lock)
        if current_weekday == lock_weekday:
            allowed_from_date = lock_date - timedelta(days=6)
        else:
            allowed_from_date = lock_date + timedelta(days=1)
        return allowed_from_date

    def _is_outside_cutoff(self):
        self.ensure_one()
        if not self.date:
            raise ValidationError(self.env._("A timesheet date is required."))
        allowed_from_date = self._get_allowed_from_date()
        return self.date < allowed_from_date

    def _validate_timesheet_lock(self):
        company = self.company_id
        if not company.timesheet_lock_weekday:
            return False
        has_bypass_group = self.env.user.has_group(
            "hr_timesheet_weekly_cutoff.group_bypass_timesheet_lock"
        )
        outside_weekly_cutoff = False
        is_outside_cutoff = self._is_outside_cutoff()
        if has_bypass_group:
            if is_outside_cutoff:
                outside_weekly_cutoff = True
        if is_outside_cutoff and not outside_weekly_cutoff:
            raise ValidationError(
                self.env._(
                    "You cannot register timesheets dated "
                    f"{fields.Date.to_string(self.date)} "
                    "due to the weekly cutoff control."
                )
            )
        return outside_weekly_cutoff

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "project_id" in vals:
                record = self.new(vals)
                weekly_cutoff = record._validate_timesheet_lock()
                vals["is_outside_weekly_cutoff"] = weekly_cutoff
        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            if record.project_id and "validated" not in vals:
                weekly_cutoff = record._validate_timesheet_lock()
                if "date" in vals:
                    record.is_outside_weekly_cutoff = weekly_cutoff
        return result
