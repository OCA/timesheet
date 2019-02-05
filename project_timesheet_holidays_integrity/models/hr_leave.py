# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.multi
    def action_restore_data_integrity_with_timesheets(self):
        AccountAnalyticLine = self.env['account.analytic.line']

        def should_map_to_timesheets(leave):
            return leave.holiday_type == 'employee' and \
                leave.holiday_status_id.timesheet_project_id and \
                leave.holiday_status_id.timesheet_task_id

        for leave in self.filtered(should_map_to_timesheets):
            if leave.timesheet_ids:
                timesheet_ids = leave.timesheet_ids
                timesheet_ids.write({'holiday_id': False})
                timesheet_ids.unlink()

            # create the timesheet on the vacation project
            holiday_project = leave.holiday_status_id.timesheet_project_id
            holiday_task = leave.holiday_status_id.timesheet_task_id

            work_hours_data = leave.employee_id.list_work_time_per_day(
                leave.date_from,
                leave.date_to,
                domain=[
                    ('holiday_id', '!=', leave.id),
                    ('time_type', '=', 'leave'),
                ]
            )
            for index, (day_date, work_hours_count) in \
                    enumerate(work_hours_data):
                AccountAnalyticLine.create({
                    'name': '%s (%s/%s)' % (
                        leave.holiday_status_id.name or '',
                        index + 1,
                        len(work_hours_data)
                    ),
                    'project_id': holiday_project.id,
                    'task_id': holiday_task.id,
                    'account_id': holiday_project.analytic_account_id.id,
                    'unit_amount': work_hours_count,
                    'user_id': leave.employee_id.user_id.id,
                    'date': day_date,
                    'holiday_id': leave.id,
                    'employee_id': leave.employee_id.id,
                })
