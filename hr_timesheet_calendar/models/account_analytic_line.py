from datetime import datetime

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

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
