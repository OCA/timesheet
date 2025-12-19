from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    break_duration = fields.Float(default=0.0)

    @api.onchange("time_start", "time_stop", "break_duration")
    def onchange_hours_start_stop(self):
        res = super().onchange_hours_start_stop()
        if self.time_start and self.time_stop and self.break_duration:
            self.unit_amount -= self.break_duration
        return res

    @api.constrains("time_start", "time_stop", "unit_amount", "break_duration")
    def _check_time_start_stop(self):
        for line in self:
            if not line.time_start and not line.time_stop:
                continue

            expected_amount = line.time_stop - line.time_start - line.break_duration

            if (
                float_compare(line.unit_amount, expected_amount, precision_digits=2)
                != 0
            ):
                # OCA standard: Uporabimo poimenovane parametre za prevajanje
                raise ValidationError(
                    _(
                        "The duration (%(duration)s) must be equal to the difference "
                        "between the hours (%(stop)s-%(start)s) minus the "
                        "break (%(break)s)."
                    )
                    % {
                        "duration": line.unit_amount,
                        "stop": line.time_stop,
                        "start": line.time_start,
                        "break": line.break_duration,
                    }
                )
