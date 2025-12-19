from odoo import api, fields, models

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    break_duration = fields.Float(string="Break Duration", default=0.0)

    @api.onchange("time_start", "time_stop", "break_duration")
    def onchange_hours_start_stop(self):
        super().onchange_hours_start_stop()
        if self.time_start and self.time_stop and self.break_duration:
            self.unit_amount -= self.break_duration
