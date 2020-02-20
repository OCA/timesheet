# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    exclude_from_employee_cost = fields.Boolean(
        string='Exclude from Employee Cost',
    )

    @api.multi
    def _get_average_hourly_cost_period_start(self, policy, as_of_date):
        """ Hook for extensions """
        self.ensure_one()
        if policy == 'annual_avg':
            return as_of_date.replace(month=1, day=1)
        elif policy == 'monthly_avg':
            return as_of_date.replace(day=1)
        return self.date_start

    @api.multi
    def _get_average_hourly_cost_period_end(self, policy, as_of_date):
        """ Hook for extensions """
        self.ensure_one()
        if policy == 'annual_avg':
            return as_of_date + relativedelta(years=1, day=1, days=-1)
        elif policy == 'monthly_avg':
            return as_of_date + relativedelta(months=1, day=1, days=-1)
        return self.date_end or as_of_date

    @api.multi
    def _compute_average_hourly_cost(self, policy, currency_id, as_of_date):
        IrModuleModule = self.env['ir.module.module']

        project_timesheet_holidays = IrModuleModule.sudo().search([
            ('name', '=', 'project_timesheet_holidays'),
            ('state', '=', 'installed'),
        ], limit=1)
        project_timesheet_holidays = self.env.context.get(
            'assume_project_timesheet_holidays_installed',
            project_timesheet_holidays
        )
        has_contract_amount = 'amount' in self._fields \
            and 'amount_period' in self._fields
        has_approximate_wage = 'approximate_wage' in self._fields \
            and 'is_wage_accurate' in self._fields
        shared_leaves_domain = [
            ('time_type', '=', 'leave'),
            ('unpaid', '!=', True),
        ]

        hourly_rates = 0.0
        for contract in self:
            if has_contract_amount and contract.amount_period == 'hour':
                hourly_rates += contract.currency_id._convert(
                    contract.amount,
                    currency_id,
                    contract.company_id,
                    as_of_date
                )
                continue

            period_start = contract._get_average_hourly_cost_period_start(
                policy,
                as_of_date,
            )
            period_end = contract._get_average_hourly_cost_period_end(
                policy,
                as_of_date,
            )
            leaves_domain = shared_leaves_domain
            if project_timesheet_holidays:
                # NOTE: If project_timesheet_holidays is adding timesheet
                # entries for leaves, use only global leaves, otherwise use
                # all paid leaves for this.
                leaves_domain += [('resource_id', '=', False)]

            if has_contract_amount and contract.amount_period == 'day':
                work_data = contract.employee_id.get_work_days_data(
                    datetime.combine(period_start, time.min),
                    datetime.combine(period_end, time.max),
                    domain=leaves_domain,
                )
                hourly_rates += contract.currency_id._convert(
                    contract.amount * work_data['days'] / work_data['hours'],
                    currency_id,
                    contract.company_id,
                    as_of_date
                )
                continue

            month_start = period_start
            months = 0
            contract_hourly_rates = 0.0
            while month_start < period_end:
                month_end = min(
                    month_start + relativedelta(months=1, day=1, days=-1),
                    period_end
                )
                hours = contract.employee_id.get_work_days_data(
                    datetime.combine(month_start, time.min),
                    datetime.combine(month_end, time.max),
                    domain=leaves_domain,
                )['hours']
                if has_approximate_wage and not contract.is_wage_accurate:
                    wage = contract.approximate_wage
                else:
                    wage = contract.wage
                contract_hourly_rates += wage / hours
                months += 1
                month_start += relativedelta(months=1, day=1)
            contract_hourly_rates = contract.currency_id._convert(
                contract_hourly_rates,
                currency_id,
                contract.company_id,
                as_of_date
            )
            hourly_rates += contract_hourly_rates / months
        return currency_id.round(hourly_rates / len(self))
