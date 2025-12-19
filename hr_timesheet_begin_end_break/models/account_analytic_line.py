from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    break_duration = fields.Float(default=0.0)

    @api.onchange("time_start", "time_stop", "break_duration")
    def onchange_hours_start_stop(self):
        res = super().onchange_hours_start_stop()
        if self.time_start and self.time_stop:
            # Re-calculate unit_amount to include break
            self.unit_amount = self.time_stop - self.time_start - self.break_duration
        return res

    @api.constrains("time_start", "time_stop", "unit_amount", "break_duration")
    def _check_time_start_stop(self):
        # We do NOT call super() here because the base module's constraint
        # does not account for break_duration and would raise a ValidationError.
        
        for line in self:
            if not line.time_start and not line.time_stop:
                continue

            # 1. Check if start is before end (Standard check)
            if line.time_start > line.time_stop:
                raise ValidationError(_("The start hour must be before the end hour."))

            # 2. Check for overlaps (Copied from base to ensure it still works)
            domain = [
                ("id", "!=", line.id),
                ("employee_id", "=", line.employee_id.id),
                ("date", "=", line.date),
                "|",
                "|",
                "&",
                ("time_start", "<=", line.time_start),
                ("time_stop", ">", line.time_start),
                "&",
                ("time_start", "<", line.time_stop),
                ("time_stop", ">=", line.time_stop),
                "&",
                ("time_start", ">=", line.time_start),
                ("time_stop", "<=", line.time_stop),
            ]
            if self.search_count(domain):
                raise ValidationError(_("You cannot have an overlap of timesheets."))

            # 3. Check duration with break (The core of this module)
            expected_amount = line.time_stop - line.time_start - line.break_duration
            if float_compare(line.unit_amount, expected_amount, precision_digits=2) != 0:
                def float_to_time(f):
                    return "%02d:%02d" % (int(f), int(round((f - int(f)) * 60)))

                raise ValidationError(
                    _(
                        "The duration (%(duration)s) must be equal to the "
                        "difference between the hours minus break (%(expected)s)."
                    )
                    % {
                        "duration": float_to_time(line.unit_amount),
                        "expected": float_to_time(expected_amount),
                    }
                )
