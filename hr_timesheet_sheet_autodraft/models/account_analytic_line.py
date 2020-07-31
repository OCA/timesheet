# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _determine_sheet(self):
        sheet = super()._determine_sheet()
        if sheet or not self.company_id.timesheet_sheets_autodraft:
            return sheet
        return self._autodraft_sheet()

    def _autodraft_sheet(self):
        """ Hook for extensions """
        self.ensure_one()
        HrTimesheetSheet = self.env["hr_timesheet.sheet"]
        if not self.env.context.get("manual_autodraft_timesheet_sheet", False):
            HrTimesheetSheet = HrTimesheetSheet.sudo()
        values = self._get_autodraft_sheet_values()
        sheet = HrTimesheetSheet.new(
            {**HrTimesheetSheet.default_get(HrTimesheetSheet._fields.keys()), **values}
        )
        existing_sheets_domain = sheet._get_overlapping_sheet_domain()
        existing_sheets_domain = list(
            filter(lambda criteria: criteria[0] != "id", existing_sheets_domain)
        )
        if HrTimesheetSheet.search(existing_sheets_domain, limit=1):
            return None
        sheet = HrTimesheetSheet.create(values)
        sheet._compute_timesheet_ids()
        return sheet

    def _get_autodraft_sheet_values(self):
        """ Hook for extensions """
        self.ensure_one()
        HrTimesheetSheet = self.env["hr_timesheet.sheet"]
        return {
            "employee_id": self.employee_id.id,
            "company_id": self.company_id.id,
            "date_start": HrTimesheetSheet._get_period_start(
                self.company_id, self.date
            ),
            "date_end": HrTimesheetSheet._get_period_end(self.company_id, self.date),
        }

    def action_autodraft_timesheet_sheets(self):
        self.filtered(lambda aal: not aal.sheet_id).with_context(
            manual_autodraft_timesheet_sheet=True
        )._compute_sheet()
