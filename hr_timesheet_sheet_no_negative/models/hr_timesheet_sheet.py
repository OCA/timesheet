# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, _


class SheetLine(models.TransientModel):
    _inherit = 'hr_timesheet.sheet.line'

    def _negative_unit_amount(self):
        if not self.sheet_id.company_id:
            if self._context.get('company_id'):
                company_id = self._context.get('company_id')
                company = self.env['res.company'].browse(company_id)
            else:
                company = self.sheet_id.employee_id.company_id
        else:
            company = self.sheet_id.company_id
        return company.timesheet_negative_unit_amount

    @api.onchange('unit_amount')
    def onchange_unit_amount(self):
        if not self._get_sheet():
            return {'warning': {
                'title': _("Warning"),
                'message': _("Save the Timesheet Sheet first.")
            }}
        if not self._negative_unit_amount() and self.unit_amount < 0.0:
            self.write({'unit_amount': 0.0})
        return super(SheetLine, self).onchange_unit_amount()

    @api.model
    def _line_to_timesheet(self, amount):
        if not self._negative_unit_amount() and amount < 0.0:
            return False
        return super(SheetLine, self)._line_to_timesheet()
