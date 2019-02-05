# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    def action_restore_data_integrity_with_leaves(self):
        for line in self.filtered('holiday_id'):
            holiday_project = (
                line.holiday_id.holiday_status_id.timesheet_project_id
            )
            holiday_task = (
                line.holiday_id.holiday_status_id.timesheet_task_id
            )
            work_hours_data = line.employee_id.list_work_time_per_day(
                line.holiday_id.date_from,
                line.holiday_id.date_to,
                domain=[
                    ('holiday_id', '!=', line.holiday_id.id),
                    ('time_type', '=', 'leave'),
                ],
            )

            for index, (day_date, work_hours_count) in \
                    enumerate(work_hours_data):
                if day_date != line.date:
                    continue

                line.with_context(
                    skip_leave_integrity_check=True,
                ).write({
                    'name': '%s (%s/%s)' % (
                        line.holiday_id.holiday_status_id.name or '',
                        index + 1,
                        len(work_hours_data)
                    ),
                    'project_id': holiday_project.id,
                    'task_id': holiday_task.id,
                    'account_id': holiday_project.analytic_account_id.id,
                    'unit_amount': work_hours_count,
                    'user_id': line.holiday_id.employee_id.user_id.id,
                    'employee_id': line.holiday_id.employee_id.id,
                })
                break

    @api.model
    def _get_leave_fields(self):
        return [
            'name',
            'project_id',
            'task_id',
            'account_id',
            'unit_amount',
            'user_id',
            'date',
            'employee_id',
        ]

    @api.multi
    def write(self, vals):
        leave_aals = self.filtered('holiday_id')
        if leave_aals and \
                not self.env.context.get('skip_leave_integrity_check', False):
            fields = list(vals.keys())
            new_values = self._convert_to_cache(
                vals,
                update=True,
                validate=False,
            )
            for old_values in leave_aals.read(fields, load='_classic_write'):
                old_values = self._convert_to_cache(
                    old_values,
                    validate=False,
                )
                for field in self._get_leave_fields():
                    if field not in fields:
                        continue
                    if new_values[field] == old_values[field]:
                        continue
                    raise UserError(_(
                        'You cannot modify timesheet lines attached to a leave'
                    ))
        return super().write(vals)
