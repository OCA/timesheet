from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class HrTimesheetReport(models.TransientModel):
    _inherit = "hr.timesheet.report"

    analytic_line_domain = fields.Char(string="Filter Timesheet")

    def _get_domain(self):
        self.ensure_one()
        query = super(HrTimesheetReport, self)._get_domain()
        if isinstance(self.analytic_line_domain, str):
            query += safe_eval(self.analytic_line_domain)
        return query
