# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

from openerp import models, fields, api, _
from openerp.fields import DATE_LENGTH
from datetime import datetime
from openerp.exceptions import ValidationError


class CrmPhonecall(models.Model):
    _inherit = 'crm.phonecall'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account')
    timesheet_ids = fields.One2many(comodel_name='hr.analytic.timesheet',
                                    inverse_name='phonecall_id')

    def _timesheet_prepare(self, vals):
        """
            param: vals
            type: dict
            desc: crm.phonecall vals dict (It's like create and write methods)
        """
        if len(self) > 0:
            self.ensure_one()
        date = vals.get('date', self.date)
        if not date:
            raise ValidationError(_('Date field must be filled.'))
        user_id = vals.get('user_id', self.user_id.id)
        account_id = vals.get('analytic_account_id',
                              self.analytic_account_id.id)
        unit_amount = vals.get('duration', self.duration)
        res = {
            'date': date[:DATE_LENGTH],
            'user_id': user_id,
            'name': vals.get('name', self.name),
            'account_id': account_id,
            'unit_amount': unit_amount / 60.0,
            'code': 'phone',
            'journal_id': self.env[
                'hr.analytic.timesheet']._getAnalyticJournal()
        }
        return res

    @api.model
    def create(self, vals):
        if vals.get('analytic_account_id') and vals.get('duration', 0) > 0:
            timesheet_data = self._timesheet_prepare(vals)
            vals['timesheet_ids'] = vals.get('timesheet_ids', [])
            vals['timesheet_ids'].append((0, 0, timesheet_data))
        res = super(CrmPhonecall, self).create(vals)
        return res

    @api.one
    def write(self, vals):
        timesheet = self.env['hr.analytic.timesheet'].search([
            ('code', '=', 'phone'), ('phonecall_id', '=', self.id)])
        analytic_account_id = vals.get('analytic_account_id',
                                       self.analytic_account_id)
        duration = vals.get('duration', 0)
        if timesheet:
            if ('analytic_account_id' in vals
                    and not vals['analytic_account_id']):
                vals['timesheet_ids'] = [(2, timesheet.id, 0)]
            else:
                vals['timesheet_ids'] = [(1, timesheet.id,
                                         self._timesheet_prepare(vals))]
        elif analytic_account_id and duration > 0:
            vals['timesheet_ids'] = [(0, 0, self._timesheet_prepare(vals))]
        res = super(CrmPhonecall, self).write(vals)
        return res

    @api.multi
    def button_end_call(self):
        end_date = datetime.now()
        for call in self:
            if call.date:
                start_date = fields.Datetime.from_string(call.date)
                call.duration = self._end_call(start_date, end_date)
        return True

    def _end_call(self, start_dt, end_dt):
        if not isinstance(start_dt, datetime):
            raise ValidationError(_('Start date must be datetime.'))
        if not isinstance(end_dt, datetime):
            raise ValidationError(_('End date must be datetime.'))
        if end_dt < start_dt:
            return 0
        return (end_dt - start_dt).total_seconds() / 60.0
