from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    break_duration = fields.Float(default=0.0)

    @api.constrains("time_start", "time_stop", "unit_amount", "break_duration")
    def _check_time_start_stop(self):
        # Call super to trigger the overlap check from the base module
        res = super()._check_time_start_stop()

        for line in self:
            if not line.time_start and not line.time_stop:
                continue

            # Calculate the expected amount: (Stop - Start) - Break
            expected_amount = line.time_stop - line.time_start - line.break_duration

            # Compare floats and break line to satisfy Ruff (length < 88)
            diff = float_compare(
                line.unit_amount, expected_amount, precision_digits=2
            )
            if diff != 0:
                # Helper to format float as HH:MM for the error message
                def float_to_time(f):
                    return "%02d:%02d" % (int(f), int(round((f - int(f)) * 60)))

                # The error message must match the format expected by the tests
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
        return res
