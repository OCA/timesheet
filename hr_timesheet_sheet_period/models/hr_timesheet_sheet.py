# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .res_company import SHEET_RANGE_PAYROLL_PERIOD


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.model
    def _default_date_start(self):
        result = super()._default_date_start()
        company = self.env['res.company']._company_default_get()
        if company.sheet_range == SHEET_RANGE_PAYROLL_PERIOD:
            period = self._get_current_pay_period()
            return period and period.date_start or result
        return result

    @api.model
    def _default_date_end(self):
        result = super()._default_date_end()
        company = self.env['res.company']._company_default_get()
        if company.sheet_range == SHEET_RANGE_PAYROLL_PERIOD:
            period = self._get_current_pay_period()
            return period and period.date_end or result
        return result

    @api.model
    def _default_hr_period_id(self):
        company = self.env['res.company']._company_default_get()
        if company.sheet_range == SHEET_RANGE_PAYROLL_PERIOD:
            return self._get_current_pay_period()
        return self.env['hr.period']

    is_hr_period_required = fields.Boolean(
        compute='_compute_hr_period_required',
    )
    hr_period_id = fields.Many2one(
        string='Pay Period',
        comodel_name='hr.period',
        readonly=True,
        states={'new': [('readonly', False)]},
        default=lambda self: self._default_hr_period_id(),
        ondelete='cascade',
    )

    @api.multi
    @api.depends('date_start', 'date_end', 'hr_period_id.name')
    def _compute_name(self):
        super()._compute_name()
        for sheet in self.filtered('hr_period_id'):
            sheet.name = sheet.hr_period_id.name

    @api.onchange('hr_period_id')
    def _onchange_hr_period_id(self):
        if self.hr_period_id:
            self.date_start = self.hr_period_id.date_start
            self.date_end = self.hr_period_id.date_end
            self.name = self.hr_period_id.name

    @api.onchange('employee_id')
    def _onchange_employee_hr_period_id(self):
        if self.company_id.sheet_range != SHEET_RANGE_PAYROLL_PERIOD:
            return
        self.hr_period_id = self._get_current_pay_period()
        self._onchange_hr_period_id()

    @api.model
    def _get_current_pay_period(self):
        HrPeriod = self.env['hr.period']
        HrContract = self.env['hr.contract']
        contract = HrContract.sudo().search([
            ('employee_id', '=', self._default_employee().id),
        ])
        today = fields.Date.today()
        search_domain = [
            ('date_start', '<=', today),
            ('date_end', '>=', today),
        ]
        if contract and contract.schedule_pay:
            search_domain += [('schedule_pay', '=', contract.schedule_pay)]
        return HrPeriod.search(search_domain, limit=1)

    @api.multi
    @api.constrains('company_id', 'hr_period_id')
    def _check_hr_period(self):
        for sheet in self:
            if sheet.company_id.sheet_range == SHEET_RANGE_PAYROLL_PERIOD \
                    and not sheet.hr_period_id:
                raise ValidationError(_('No suitable Payroll period found!'))

    @api.multi
    @api.constrains('hr_period_id', 'date_start', 'date_end')
    def _check_hr_period_dates(self):
        for timesheet in self.filtered('hr_period_id'):
            if timesheet.date_start != timesheet.hr_period_id.date_start:
                raise ValidationError(
                    _("The Date From of Timesheet must match with that of"
                        " date start '%s' of the Payroll period '%s'.") % (
                        timesheet.hr_period_id.date_start,
                        timesheet.hr_period_id.name))
            if timesheet.date_end != timesheet.hr_period_id.date_end:
                raise ValidationError(
                    _("The Date To of Timesheet must match with that of"
                        " date stop '%s' of the Payroll period '%s'.") % (
                        timesheet.hr_period_id.date_end,
                        timesheet.hr_period_id.name))

    @api.depends('company_id.sheet_range')
    def _compute_hr_period_required(self):
        for sheet in self:
            sheet.is_hr_period_required = \
                sheet.company_id.sheet_range == SHEET_RANGE_PAYROLL_PERIOD
