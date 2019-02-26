# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    sheet_id = fields.Many2one(
        comodel_name='hr_timesheet.sheet',
        string='Sheet',
    )

    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet"""
        for timesheet in self:
            if not timesheet.project_id:
                continue
            sheet = self.env['hr_timesheet.sheet'].search([
                ('date_end', '>=', timesheet.date),
                ('date_start', '<=', timesheet.date),
                ('employee_id', '=', timesheet.employee_id.id),
                ('company_id', 'in', [timesheet.company_id.id, False]),
                ('state', '=', 'draft'),
            ], limit=1)
            if timesheet.sheet_id != sheet:
                timesheet.sheet_id = sheet

    @api.model
    def create(self, values):
        res = super(AccountAnalyticLine, self).create(values)
        res._compute_sheet()
        return res

    @api.multi
    def write(self, values):
        self._check_state_on_write(values)
        res = super(AccountAnalyticLine, self).write(values)
        vals_do_compute = ['date', 'employee_id', 'project_id', 'company_id']
        if any(val in vals_do_compute for val in values):
            self._compute_sheet()
        return res

    @api.multi
    def unlink(self):
        self._check_state()
        return super(AccountAnalyticLine, self).unlink()

    @api.multi
    def _check_state_on_write(self, values):
        """ This method must allow validation of invoices if
        the timesheet sheet is not in draft state. In sale_timesheet addon,
        the `_compute_timesheet_revenue` method of `account.invoice` model
        modifies the `timesheet_revenue` and `timesheet_invoice_id` fields in
        analytic lines.
        """
        allowed = self._get_allowed_fields_on_check_state()
        if any(val not in allowed for val in values):
            self._check_state()

    def _get_allowed_fields_on_check_state(self):
        """ Extend this method to add fields that could be modified
        when the timesheet sheet is not in draft.
        """
        return [
            'timesheet_invoice_id',
            'timesheet_revenue',
            'product_uom_id',
            'amount'
        ]

    @api.multi
    def _check_state(self):
        if self.env.context.get('skip_check_state'):
            return
        for line in self:
            if line.sheet_id and line.sheet_id.state != 'draft':
                raise UserError(
                    _('You cannot modify an entry in a confirmed '
                      'timesheet sheet.'))

    @api.multi
    def merge_timesheets(self):
        unit_amount = sum(
            [t.unit_amount for t in self])
        amount = sum([t.amount for t in self])
        self[0].write({
            'unit_amount': unit_amount,
            'amount': amount,
        })
        self[1:].unlink()
        return self[0]
