# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.osv.expression import TRUE_DOMAIN
from odoo.tools.safe_eval import safe_eval


class HrTimesheetReportEntry(models.TransientModel):
    _inherit = "hr.timesheet.report.entry"

    def _compute_total_unit_amount(self):
        AccountAnalyticLine = self.env["account.analytic.line"]
        uom_hour = self.env.ref("uom.product_uom_hour")

        for entry in self:
            total_unit_amount = 0.0
            line_ids = AccountAnalyticLine.search(
                safe_eval(entry.scope) if entry.scope else TRUE_DOMAIN
            )
            for line_id in line_ids:
                total_unit_amount += line_id.product_uom_id._compute_quantity(
                    line_id.unit_amount_rounded, uom_hour
                )
            entry.total_unit_amount = total_unit_amount
