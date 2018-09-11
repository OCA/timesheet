# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    sheet_id_computed = fields.Many2one(
        comodel_name='hr_timesheet.sheet',
        string='Sheet',
        compute='_compute_sheet',
        index=True,
        ondelete='cascade',
        search='_search_sheet'
    )
    sheet_id = fields.Many2one(
        comodel_name='hr_timesheet.sheet',
        string='Sheet',
        compute='_compute_sheet',
        store=True,
    )

    @api.depends('date', 'user_id', 'project_id', 'task_id', 'company_id',
                 'sheet_id.date_start', 'sheet_id.date_end',
                 'sheet_id.employee_id', 'sheet_id.company_id')
    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet"""
        for timesheet in self:
            if timesheet.sheet_id or not timesheet.project_id:
                continue
            sheets = self.env['hr_timesheet.sheet'].search(
                [('date_end', '>=', timesheet.date),
                 ('date_start', '<=', timesheet.date),
                 ('employee_id.user_id.id', '=', timesheet.user_id.id),
                 ('company_id', 'in', [timesheet.company_id.id, False]),
                 ('state', '=', 'draft'),
                 ])
            if sheets:
                timesheet.sheet_id_computed = sheets[0]
                timesheet.sheet_id = sheets[0]

    def _search_sheet(self, operator, value):
        assert operator == 'in'
        ids = []
        for ts in self.env['hr_timesheet.sheet'].browse(value):
            self._cr.execute("""
                    SELECT l.id
                        FROM account_analytic_line l
                    WHERE %(date_end)s >= l.date
                        AND %(date_start)s <= l.date
                        AND %(user_id)s = l.user_id
                        AND %(company_id)s = l.company_id
                    GROUP BY l.id""", {'date_start': ts.date_start,
                                       'date_end': ts.date_end,
                                       'user_id': ts.employee_id.user_id.id,
                                       'company_id': ts.company_id.id,
                                       })
            ids.extend([row[0] for row in self._cr.fetchall()])
        return [('id', 'in', ids)]

    @api.multi
    def write(self, values):
        self._check_state_on_write(values)
        return super(AccountAnalyticLine, self).write(values)

    @api.multi
    def unlink(self):
        self._check_state()
        return super(AccountAnalyticLine, self).unlink()

    @api.multi
    def _check_state_on_write(self, values):
        """ Hook for extensions """
        self._check_state()

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
