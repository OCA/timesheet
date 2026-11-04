from odoo import api, models

empty_name = "/"


class SheetNewAnalyticLine(models.TransientModel):
    _name = "hr_timesheet.sheet.new.analytic.line"
    _inherit = "hr_timesheet.sheet.line.abstract"
    _description = "Timesheet Sheet New Analytic Line"

    @api.model
    def _is_similar_analytic_line(self, aal):
        """Hook for extensions"""
        return (
            aal.date == self.date
            and aal.project_id.id == self.project_id.id
            and aal.task_id.id == self.task_id.id
        )

    @api.model
    def _update_analytic_lines(self):
        sheet = self.sheet_id
        timesheets = sheet.timesheet_ids.filtered(
            lambda aal: self._is_similar_analytic_line(aal)
        )
        new_ts = timesheets.filtered(lambda t: t.name == empty_name)
        amount = sum(t.unit_amount for t in timesheets)
        diff_amount = self.unit_amount - amount
        if len(new_ts) > 1:
            new_ts = new_ts.merge_timesheets()
            sheet._sheet_write("timesheet_ids", sheet.timesheet_ids.exists())
        if not diff_amount:
            return
        if new_ts:
            unit_amount = new_ts.unit_amount + diff_amount
            if unit_amount:
                new_ts.write({"unit_amount": unit_amount})
            else:
                new_ts.unlink()
                sheet._sheet_write("timesheet_ids", sheet.timesheet_ids.exists())
        else:
            new_ts_values = sheet._prepare_new_line(self)
            new_ts_values.update({"name": empty_name, "unit_amount": diff_amount})
            self.env["account.analytic.line"]._sheet_create(new_ts_values)
