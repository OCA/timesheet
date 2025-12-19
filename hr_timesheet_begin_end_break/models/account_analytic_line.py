from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    break_duration = fields.Float(default=0.0)

    @api.onchange("time_start", "time_stop", "break_duration")
    def onchange_hours_start_stop(self):
        # Izvedemo osnovni izračun iz starševskega modula (stop - start)
        res = super().onchange_hours_start_stop()
        # Odštejemo še našo pavzo
        if self.time_start and self.time_stop and self.break_duration:
            self.unit_amount -= self.break_duration
        return res

    @api.constrains("time_start", "time_stop", "unit_amount", "break_duration")
    def _check_time_start_stop(self):
        """
        Povozimo originalno metodo iz hr_timesheet_begin_end, 
        da vključimo pavzo v izračun.
        """
        for line in self:
            if not line.time_start and not line.time_stop:
                continue
            
            # Formula: Stop - Start - Pavza
            expected_amount = line.time_stop - line.time_start - line.break_duration
            
            # Primerjamo unit_amount z našo novo pričakovano vrednostjo
            if float_compare(line.unit_amount, expected_amount, precision_digits=2) != 0:
                raise ValidationError(
                    "The duration (%s) must be equal to the difference between the "
                    "hours (%s-%s) minus the break (%s)."
                    % (line.unit_amount, line.time_stop, line.time_start, line.break_duration)
                )
