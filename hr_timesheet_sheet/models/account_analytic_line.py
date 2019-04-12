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

    def _check_sheet_company_id(self, sheet_id):
        self.ensure_one()
        sheet = self.env['hr_timesheet.sheet'].browse(sheet_id)
        if sheet.company_id and sheet.company_id != self.company_id:
            raise UserError(
                _('You cannot create a timesheet of a different company '
                  'than the one of the timesheet sheet.'))

    @api.model
    def create(self, values):
        res = super(AccountAnalyticLine, self).create(values)
        res._check_sheet_company_id(values.get('sheet_id'))
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
        self[0].write({
            'unit_amount': unit_amount,
            'amount': amount,
        })
        self[1:].unlink()
        return self[0]
