# Copyright 2018 ForgeFlow, S.L.
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    sheet_id = fields.Many2one(
        comodel_name="hr_timesheet.sheet", string="Sheet", readonly=True
    )

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
            A.sheet_id AS sheet_id
        """
        )
