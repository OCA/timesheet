# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    use_manual_timesheet_cost = fields.Boolean(
        string='Use manual Timesheet Cost',
        default=lambda self: self._default_use_manual_timesheet_cost(),
    )
    timesheet_cost = fields.Monetary(
        compute='_compute_timesheet_cost',
        inverse='_inverse_timesheet_cost',
        default=None,
    )
    timesheet_cost_contracts = fields.Monetary(
        string='Timesheet Cost (contracts)',
        compute='_compute_timesheet_cost_contracts',
    )
    timesheet_cost_manual = fields.Monetary(
        string='Timesheet Cost (manual)',
    )

    @api.model
    def _default_use_manual_timesheet_cost(self):
        company = self.env['res.company'].browse(
            self.env.context.get('company_id', self.env.user.company_id.id)
        )
        return company.use_manual_employee_timesheet_cost

    @api.model
    def create(self, vals):
        if 'use_manual_timesheet_cost' not in vals:
            company = self.env.user.company_id
            if 'company_id' in vals:
                company = self.env['res.company'].browse(vals['company_id'])
            vals['use_manual_timesheet_cost'] = (
                company.use_manual_employee_timesheet_cost
            )

        if vals.get('use_manual_timesheet_cost'):
            if 'timesheet_cost' not in vals:
                vals['timesheet_cost'] = 0.0
            return super().create(vals)
        else:
            if 'timesheet_cost' in vals:
                del vals['timesheet_cost']
            return super(
                HrEmployee,
                self.with_context(inverse_timesheet_cost_nocheck=True)
            ).create(vals)

    @api.multi
    @api.depends(
        'use_manual_timesheet_cost',
        'timesheet_cost_manual',
        'currency_id',
        'contract_ids.state',
        'contract_ids.date_start',
        'contract_ids.date_end',
        'contract_ids.wage',
        'contract_ids.currency_id',
    )
    def _compute_timesheet_cost(self):
        for employee in self:
            if employee.use_manual_timesheet_cost:
                employee.timesheet_cost = employee.timesheet_cost_manual
            else:
                employee.timesheet_cost = employee.timesheet_cost_contracts

    @api.multi
    @api.depends(
        'currency_id',
        'contract_ids.state',
        'contract_ids.date_start',
        'contract_ids.date_end',
        'contract_ids.wage',
        'contract_ids.currency_id',
    )
    def _compute_timesheet_cost_contracts(self):
        as_of_date = fields.Date.today()
        for employee in self:
            employee.timesheet_cost_contracts = employee._get_timesheet_cost(
                as_of_date,
            )

    @api.multi
    def _inverse_timesheet_cost(self):
        inverse_timesheet_cost_nocheck = self.env.context.get(
            'inverse_timesheet_cost_nocheck'
        )
        as_of_date = fields.Date.today()
        for employee in self:
            if employee.use_manual_timesheet_cost:
                employee.timesheet_cost_manual = employee.timesheet_cost
            elif not inverse_timesheet_cost_nocheck \
                    and employee.timesheet_cost != employee._get_timesheet_cost(
                        as_of_date,
                    ):
                raise UserError(_(
                    'You should not set Timesheet Cost for employees that have'
                    ' it computed based on contracts.'
                ))

    @api.multi
    def _get_timesheet_cost(self, as_of_date):
        """ Hook for extensions """
        self.ensure_one()
        contracts = self.sudo()._get_timesheet_cost_contracts(as_of_date)
        if not contracts:
            return 0.0
        return contracts._compute_average_hourly_cost(
            self.company_id.employee_timesheet_cost_policy,
            self.currency_id,
            as_of_date,
        )

    @api.multi
    def _get_timesheet_cost_contracts(self, as_of_date):
        """ Hook for extensions """
        return self.env['hr.contract'].search(
            self._get_timesheet_cost_contracts_domain(as_of_date)
        )

    @api.multi
    def _get_timesheet_cost_contracts_domain(self, as_of_date):
        """ Hook for extensions """
        return [
            ('employee_id', 'in', self.ids),
            ('exclude_from_employee_cost', '!=', True),
            ('state', 'in', ['open', 'pending', 'close']),
            ('date_start', '<=', as_of_date),
            '|', ('date_end', '>=', as_of_date), ('date_end', '=', False),
        ]

    @api.onchange('use_manual_timesheet_cost')
    def onchange_use_manual_timesheet_cost(self):
        if self.use_manual_timesheet_cost:
            self.timesheet_cost = self.timesheet_cost_manual
        else:
            self.timesheet_cost = self.timesheet_cost_contracts
