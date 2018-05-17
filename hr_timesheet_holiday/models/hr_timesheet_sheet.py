# -*- coding: utf-8 -*-
# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    @api.multi
    def write(self, vals):
        result = super(HrTimesheetSheet, self).write(vals)
        if vals.get('state') == 'done':
            self._timesheet_approved()
        return result

    @api.multi
    def _timesheet_approved(self):
        requests = []
        for this in self:
            holiday2hours = {}
            for line in this.mapped('timesheet_ids'):
                holiday = line.account_id.holiday_status_ids[:1]
                if not holiday or line.leave_id:
                    continue
                holiday2hours.setdefault(holiday, 0.0)
                holiday2hours[holiday] += line.unit_amount
            for holiday, hours in holiday2hours.iteritems():
                request = self.env['hr.holidays'].sudo(this.user_id).create({
                    'name': '%s: %s' % (this.display_name, holiday.name),
                    'user_id': this.user_id.id,
                    'date_from': this.date_from,
                    'date_to': this.date_to,
                    'holiday_status_id': holiday.id,
                    'number_of_days_temp':
                    hours / self.env['hr.holidays']._get_hours_per_day(
                        this.employee_id.company_id, this.employee_id,
                    ),
                    'type': 'remove',
                    'holiday_type': 'employee',
                })
                request.signal_workflow('confirm')
                request.sudo(self.env.user).signal_workflow('validate')
                request.sudo(self.env.user).signal_workflow('second_validate')
                # circumvent all constraints here
                self.env.cr.execute(
                    'update hr_analytic_timesheet '
                    'set leave_id=%s where id in %s',
                    (request.id, tuple(this.mapped('timesheet_ids').ids)),
                )
                requests.append(request)
        return requests
