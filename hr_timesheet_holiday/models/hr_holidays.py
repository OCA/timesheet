# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class HrHolidays(models.Model):
    """Update analytic lines on status change of Leave Request"""
    _inherit = 'hr.holidays'

    # Timesheet entry linked to this leave request
    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line',
        inverse_name='leave_id',
        string='Analytic Lines',
    )

    @api.multi
    def add_timesheet_line(self, description, date, hours, account):
        """Add a timesheet line for this leave"""
        self.ensure_one()
        projects = account.project_ids.filtered(
            lambda p: p.active is True)
        if not projects:
            raise UserError('No active projects for this Analytic Account')
        self.sudo().with_context(force_write=True).write(
            {'analytic_line_ids': [(0, False, {
                'name': description,
                'date': date,
                'unit_amount': hours,
                'company_id': self.employee_id.company_id.id,
                'account_id': account.id,
                'project_id': projects[0].id,
            })]})

    @api.model
    def _get_hours_per_day(self, company, employee):
        """Can be overridden to consider employee details also"""
        hours_per_day = company.timesheet_hours_per_day
        if not hours_per_day:
            raise UserError(
                _("No hours per day defined for Company '%s'") %
                (company.name,))
        return hours_per_day

    @api.multi
    def action_approve(self):
        """On grant of leave, add timesheet lines"""
        res = super(HrHolidays, self).action_approve()

        # Postprocess Leave Types that have an analytic account configured
        for leave in self:
            account = leave.holiday_status_id.analytic_account_id
            if not account or leave.type != 'remove':
                # we only work on leaves (type=remove, type=add is allocation)
                # which have an account set
                continue

            # Assert hours per working day
            employee = leave.employee_id
            company = employee.company_id
            hours_per_day = self._get_hours_per_day(company, employee)

            # Assert user connected to employee
            user = leave.employee_id.user_id
            if not user:
                raise UserError(
                    _("No user defined for Employee '%s'") %
                    (leave.employee_id.name,))

            # Add analytic lines for these leave hours
            leave.analytic_line_ids.sudo(user.id).unlink()  # to be sure
            dt_from = fields.Datetime.from_string(leave.date_from)
            for day in range(abs(int(leave.number_of_days))):
                dt_current = dt_from + timedelta(days=day)

                # skip the non work days
                day_of_the_week = dt_current.isoweekday()
                if day_of_the_week in (6, 7):
                    continue
                leave.add_timesheet_line(
                    description=leave.name or leave.holiday_status_id.name,
                    date=dt_current,
                    hours=hours_per_day,
                    account=account,
                )

        return res

    @api.multi
    def action_refuse(self):
        """On refusal of leave, delete timesheet lines"""
        res = super(HrHolidays, self).action_refuse()
        self.mapped('analytic_line_ids').with_context(
            force_write=True).unlink()
        return res
