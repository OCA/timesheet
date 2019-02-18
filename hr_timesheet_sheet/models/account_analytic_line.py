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
                ('state', 'in', ['new', 'draft']),
            ], limit=1)
            if timesheet.sheet_id != sheet:
                timesheet.sheet_id = sheet

    @api.onchange('unit_amount')
    def onchange_unit_amount(self):
        """ Hook for extensions """

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
        vals_do_lines_compute = [
            'unit_amount', 'name',
        ]
        if not self.env.context.get('timesheet_write') and \
                any(val in vals_do_lines_compute for val in values):
            self.mapped('sheet_id').with_context(
                sheet_write=True)._onchange_timesheets()
        return res

    @api.multi
    def unlink(self):
        self._check_state()
        sheets = self.mapped('sheet_id')
        res = super(AccountAnalyticLine, self).unlink()
        sheets.with_context(sheet_write=True)._compute_line_ids()
        return res

    @api.multi
    def _check_state_on_write(self, values):
        """ Hook for extensions """
        if self._timesheet_should_check_write(values):
            self._check_state()

    @api.model
    def _timesheet_should_check_write(self, values):
        """ Hook for extensions """
        return bool(set(self._get_timesheet_protected_fields()) &
                    set(values.keys()))

    @api.model
    def _get_timesheet_protected_fields(self):
        """ Hook for extensions """
        return [
            'name',
            'date',
            'unit_amount',
            'user_id',
            'employee_id',
            'department_id',
            'company_id',
            'task_id',
            'project_id',
            'sheet_id',
        ]

    @api.multi
    def _check_state(self):
        if self.env.context.get('skip_check_state'):
            return
        for line in self:
            if line.sheet_id and line.sheet_id.state not in ['new', 'draft']:
                raise UserError(
                    _('You cannot modify an entry in a confirmed '
                      'timesheet sheet.'))

    @api.multi
    def merge_timesheets(self):
        unit_amount = sum(
            [t.unit_amount for t in self])
        amount = sum([t.amount for t in self])
        first_ts = fields.first(self)
        first_ts.with_context(timesheet_write=True).write({
            'unit_amount': unit_amount,
            'amount': amount,
        })
        others = self - first_ts
        others.unlink()
        return first_ts
