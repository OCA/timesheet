# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError as UserError


class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    @api.model
    def _default_date_from(self):
        res = super(HrTimesheetSheet, self)._default_date_from()
        period = self._get_current_pay_period()
        if period:
            return period.date_start
        else:
            return res

    @api.model
    def _default_date_to(self):
        res = super(HrTimesheetSheet, self)._default_date_to()
        period = self._get_current_pay_period()
        if period:
            return period.date_end
        else:
            return res

    @api.model
    def _default_hr_period_id(self):
        return self._get_current_pay_period()

    hr_period_id = fields.Many2one('hr.period', string='Pay Period',
                                   readonly=True,
                                   states={'new': [('readonly', False)]},
                                   default=_default_hr_period_id)
    date_from = fields.Date('Date from', required=True, index=True,
                            readonly=True,
                            states={'new': [('readonly', False)]},
                            default=_default_date_from)
    date_to = fields.Date('Date to', required=True, index=True, readonly=True,
                          states={'new': [('readonly', False)]},
                          default=_default_date_to)

    @api.multi
    def name_get(self):
        if not self._ids:
            return []
        if isinstance(self._ids, (long, int)):
            self._ids = [self._ids]
        res = super(HrTimesheetSheet, self).name_get()
        res2 = []
        for record in res:
            sheet = self.browse(record[0])
            if sheet.hr_period_id:
                record = list(record)
                name = sheet.hr_period_id.name
                record[1] = name
                res2.append(tuple(record))
            else:
                res2.append(record)
        return res2

    @api.multi
    @api.onchange('hr_period_id')
    def onchange_pay_period(self):
        if self.hr_period_id:
            self.date_from = self.hr_period_id.date_start
            self.date_to = self.hr_period_id.date_end
            self.name = self.hr_period_id.name

    @api.model
    def _get_current_pay_period(self):
        period_obj = self.env['hr.period']
        contract_obj = self.env['hr.contract']
        date_today = datetime.today().strftime('%Y-%m-%d')
        employee = self.default_get(['employee_id'])
        contract = contract_obj.search([('employee_id', '=',
                                         employee.get('employee_id'))])
        search_domain = [('date_start', '<=', date_today),
                         ('date_end', '>=', date_today)]
        if contract and contract.schedule_pay:
            search_domain += [('schedule_pay', '=', contract.schedule_pay)]
        period_ids = period_obj.search(search_domain)
        if period_ids:
            return period_ids[0]
        else:
            return False

    @api.multi
    @api.constrains('date_from', 'date_to', 'hr_period_id')
    def _check_start_end_dates(self):
        for timesheet in self:
            if timesheet.hr_period_id:
                if timesheet.date_from != timesheet.hr_period_id.date_start:
                    raise UserError(
                        _("The Date From of Timesheet must match with that of"
                          " date start '%s' of the Payroll period '%s'.") % (
                            timesheet.hr_period_id.date_start,
                            timesheet.hr_period_id.name))
                if timesheet.date_to != timesheet.hr_period_id.date_end:
                    raise UserError(
                        _("The Date To of Timesheet must match with that of"
                          " date stop '%s' of the Payroll period '%s'.") % (
                            timesheet.hr_period_id.date_end,
                            timesheet.hr_period_id.name))
