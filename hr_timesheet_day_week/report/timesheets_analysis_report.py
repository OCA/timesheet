# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models

from ..models.account_analytic_line import WEEKDAYS


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    day_week = fields.Selection(WEEKDAYS, string="Day of Week", readonly=True)

    def _select(self):
        return super()._select() + ", A.day_week AS day_week"
