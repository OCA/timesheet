from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class HrTimesheetReportWizard(models.TransientModel):
    _inherit = "hr.timesheet.report.wizard"

    analytic_line_domain = fields.Char(string="Filter Timesheet")

    def _collect_report_values(self):
        self.ensure_one()
        res = super(HrTimesheetReportWizard, self)._collect_report_values()
        if isinstance(self.analytic_line_domain, str):
            res.update({"analytic_line_domain": safe_eval(self.analytic_line_domain)})
        return res
