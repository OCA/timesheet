# Copyright 2025 APSL-Nagarro Miquel Pascual
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    exclude_from_sale_order = fields.Boolean(
        string="Non-billable",
        help="Checking this would exclude this timesheet entry from " "Sale Order",
        groups="sale_timesheet_line_exclude.group_exclude_from_sale_order",
        readonly=True,
    )

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
            A.exclude_from_sale_order AS exclude_from_sale_order
        """
        )
