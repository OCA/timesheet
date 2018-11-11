# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    can_use_timetracker = fields.Boolean(
        string='Can Track Time',
        compute='_compute_can_use_timetracker',
    )
    is_timetracker_running = fields.Boolean(
        string='Timetracker Running',
        compute='_compute_is_timetracker_running',
    )

    @api.depends('project_id', 'allow_timesheets')
    def _compute_can_use_timetracker(self):
        for task in self:
            task.can_use_timetracker = task._can_use_timetracker()

    @api.depends('timesheet_ids.is_timetracker_running')
    def _compute_is_timetracker_running(self):
        AccountAnalyticLine = self.env['account.analytic.line']
        user_id = AccountAnalyticLine._default_user()

        for task in self:
            task.is_timetracker_running = bool(AccountAnalyticLine.search([
                ('task_id', '=', task.id),
                ('user_id', '=', user_id),
                ('is_timetracker_running', '=', True),
            ], limit=1))

    def _can_use_timetracker(self):
        return self.allow_timesheets

    @api.multi
    def action_start_timetracker(self):
        self.ensure_one()

        AccountAnalyticLine = self.env['account.analytic.line']

        user_id = AccountAnalyticLine._default_user()
        form_view = self.env.ref(
            'hr_timesheet_timetracker.hr_timesheet_line_form_via_task'
        )

        actions = []

        active_timetrackers = AccountAnalyticLine.search([
            ('user_id', '=', user_id),
            ('is_timetracker_running', '=', True),
        ])
        if active_timetrackers:
            active_timetrackers._stop_timetracking(
                fields.Datetime.now()
            )
            self.env.user.notify_info(_('Timetracking stopped'))
            actions.append({
                'type': 'ir.actions.act_view_reload',
            })

        actions.append({
            'name': _('Start Timetracker'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.analytic.line',
            'views': [
                (form_view.id, 'form'),
            ],
            'view_id': form_view.id,
            'target': 'new',
            'context': {
                'default_project_id': self.project_id.id,
                'default_task_id': self.id,
                'default_timetracker_started_at': fields.Datetime.now(),
            },
        })

        return {
            'type': 'ir.actions.act_multi',
            'actions': actions,
        }

    @api.multi
    def action_stop_timetracker(self):
        self.ensure_one()

        AccountAnalyticLine = self.env['account.analytic.line']

        user_id = AccountAnalyticLine._default_user()
        now = fields.Datetime.now()

        for task in self:
            AccountAnalyticLine.search([
                ('task_id', '=', task.id),
                ('user_id', '=', user_id),
                ('is_timetracker_running', '=', True),
            ])._stop_timetracking(now)

        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def action_refresh_timetracker(self):  # pragma: no cover
        return {
            'type': 'ir.actions.act_view_reload',
        }
