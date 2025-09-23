# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

WEEKDAYS = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    day_week = fields.Selection(
        WEEKDAYS, compute="_compute_week_day", store=True, string="Day of Week"
    )

    @api.depends("date")
    def _compute_week_day(self):
        for record in self:
            week_day = record.date.weekday()
            record.day_week = str(week_day)
