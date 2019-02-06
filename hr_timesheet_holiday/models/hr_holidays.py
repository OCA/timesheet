# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from dateutil.rrule import rrule, DAILY

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
    def _prepare_account_analytic_line_value(
            self, description, date, hours, project, account):
        """ Prepare the value used to create one analytic line
        """
        self.ensure_one()
        return {
            'user_id': self.employee_id.user_id.id,
            'name': description,
            'date': date,
            'unit_amount': hours,
            'company_id': self.employee_id.company_id.id,
            'account_id': account.id,
            'project_id': project.id,
        }

    @api.multi
    def add_timesheet_line(self, description, date, hours, account):
        """Add a timesheet line for this leave"""
        self.ensure_one()
        projects = account.project_ids.filtered(
            lambda p: p.active is True)
        if not projects:
            raise UserError(_('No active projects for this Analytic Account'))
        value = self._prepare_account_analytic_line_value(
            description=description,
            date=date,
            hours=hours,
            project=projects[0],
            account=account,
        )
        self.sudo().with_context(force_write=True).write(
            {'analytic_line_ids': [(0, False, value)]})

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
    def _get_analytic_account(self):
        """Return the analytic account to use to create the analytic account
        lines"""
        self.ensure_one()
        return self.holiday_status_id.analytic_account_id

    @api.multi
    def action_approve(self):
        """On grant of leave, add timesheet lines"""
        res = super(HrHolidays, self).action_approve()

        # Postprocess Leave Types that have an analytic account configured
        for leave in self:
            account = leave._get_analytic_account()
            if not account or leave.type != 'remove':
                # we only work on leaves (type=remove, type=add is allocation)
                # which have an account set
                continue
            leave._create_or_update_analytic_lines(account)
        return res

    @api.multi
    def _create_or_update_analytic_lines(self, analytic_account):
        self.ensure_one()
        # Assert user connected to employee
        user = self.employee_id.user_id
        if not user:
            raise UserError(
                _("No user defined for Employee '%s'") %
                (self.employee_id.name,))
        self.analytic_line_ids.sudo(user.id).unlink()  # to be sure

        if self.employee_id.calendar_id and \
                self.employee_id.company_id.timesheet_holiday_use_calendar:
            self._create_analytic_lines_for_calendar(analytic_account)
        else:
            self._create_analytic_lines(analytic_account)

    @api.multi
    def _create_analytic_lines(self, analytic_account):
        """ Create the analytic lines based on a fixed amount of working
        hours per day and a Monday to Friday shift
        """
        self.ensure_one()
        # Assert hours per working day
        employee = self.employee_id
        company = employee.company_id
        hours_per_day = self._get_hours_per_day(company, employee)

        # Add analytic lines for these leave hours
        dt_from = fields.Datetime.from_string(self.date_from)
        for day in range(abs(int(self.number_of_days))):
            dt_current = dt_from + timedelta(days=day)

            # skip the non work days
            day_of_the_week = dt_current.isoweekday()
            if day_of_the_week in (6, 7):
                continue
            self.add_timesheet_line(
                description=self.name or self.holiday_status_id.name,
                date=dt_current,
                hours=hours_per_day,
                account=analytic_account,
            )

    @api.multi
    def _create_analytic_lines_for_calendar(self, analytic_account):
        """ Create the analytic lines based on the working time schedule
        linked to the employee
        """
        self.ensure_one()
        calendar = self.employee_id.calendar_id.sudo(self.employee_id.user_id)
        for start_dt, end_dt in self._iter_leave_days():
            hours = calendar.get_working_hours_of_date(
                start_dt=start_dt,
                end_dt=end_dt,
                compute_leaves=False,
                resource_id=self.employee_id.id,
            )
            self.add_timesheet_line(
                description=self.name or self.holiday_status_id.name,
                date=start_dt,
                hours=hours,
                account=analytic_account
            )

    @api.multi
    def _iter_leave_days(self):
        """
        An iterator over leave days.
        :return: a tuple start_dt, end_dt
        """
        self.ensure_one()
        datetime_from = fields.Datetime.from_string(self.date_from)
        datetime_to = fields.Datetime.from_string(self.date_to)
        date_from = fields.Date.from_string(self.date_from)
        date_to = fields.Date.from_string(self.date_to)

        for d in rrule(
            dtstart=date_from, interval=1, until=date_to, freq=DAILY
        ):
            if d.date() == date_from:
                dt_from = datetime_from
            else:
                dt_from = d.replace(hour=0, minute=0, second=0, microsecond=0)
            if d.date() == date_to:
                dt_to = datetime_to
            else:
                dt_to = d.replace(
                    hour=23, minute=59, second=59, microsecond=999999)
            yield dt_from, dt_to

    @api.multi
    def action_refuse(self):
        """On refusal of leave, delete timesheet lines"""
        res = super(HrHolidays, self).action_refuse()
        self.mapped('analytic_line_ids').with_context(
            force_write=True).unlink()
        return res
