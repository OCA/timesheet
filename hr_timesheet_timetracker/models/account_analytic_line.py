# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'date desc, create_date desc, id desc'

    create_date = fields.Datetime(
        index=True,
    )
    is_timetracker_running = fields.Boolean(
        string='Timetracker Running',
        compute='_compute_is_timetracker_running',
        store=True,
    )
    is_timetracked = fields.Boolean(
        string='Timetracked Line',
        compute='_compute_is_timetracked',
        store=True,
    )
    timetracker_started_at = fields.Datetime(
        string='Started At',
        copy=False,
        index=True,
        help='Timestamp when timetracker was started',
        track_visibility='onchange',
    )
    timetracker_stopped_at = fields.Datetime(
        string='Stopped At',
        copy=False,
        index=True,
        help='Timestamp when timetracker was stopped',
        track_visibility='onchange',
    )
    can_use_timetracker = fields.Boolean(
        string='Can Track Time',
        compute='_compute_can_use_timetracker',
    )

    _sql_constraints = [
        (
            'single_running_timetracker_per_employee',
            (
                'EXCLUDE (employee_id WITH =) WHERE ('
                '    timetracker_started_at IS NOT NULL'
                '    AND timetracker_stopped_at IS NULL'
                ')'
            ),
            'Only one running timetracker allowed per employee'
        ),
        (
            'timetracker_start_before_stop',
            'CHECK (timetracker_stopped_at >= timetracker_started_at)',
            (
                'Timetracking can not be stopped earlier than has been'
                ' started'
            )
        ),
        (
            'timetracker_nostart_but_stop',
            (
                'CHECK ('
                '    ('
                '        timetracker_stopped_at IS NOT NULL'
                '            AND timetracker_started_at IS NOT NULL'
                '    ) OR timetracker_stopped_at IS NULL'
                ')'
            ),
            (
                'Timetracking can not be stopped without being previously'
                ' started'
            )
        ),
    ]

    @api.depends('timetracker_started_at', 'timetracker_stopped_at')
    def _compute_is_timetracker_running(self):
        for line in self:
            line.is_timetracker_running = (
                line.timetracker_started_at and not line.timetracker_stopped_at
            )

    @api.depends('timetracker_started_at')
    def _compute_is_timetracked(self):
        for line in self:
            line.is_timetracked = (
                True if line.timetracker_started_at else False
            )

    @api.depends('user_id', 'employee_id', 'employee_id.user_id')
    def _compute_can_use_timetracker(self):
        for line in self:
            line.can_use_timetracker = line._can_use_timetracker()

    @api.onchange('user_id', 'employee_id')
    def _onchange_employee_id(self):
        self.can_use_timetracker = self._can_use_timetracker()

    def _can_use_timetracker(self):
        return self.employee_id.user_id.id == self._default_user()

    @api.multi
    def _start_timetracking(self, timestamp):
        self.write({
            'timetracker_started_at': timestamp,
        })

    @api.multi
    def _stop_timetracking(self, timestamp):
        self.write({
            'timetracker_stopped_at': timestamp,
        })

    @api.multi
    def toggle_timetracker(self):
        now = fields.Datetime.now()

        affected_lines = []
        for line in self:
            if line.is_timetracker_running:
                # In case tracking is active, just stop it
                line._stop_timetracking(now)
                affected_lines.append(line)
            elif not line.timetracker_started_at and \
                    line.unit_amount == 0.0:
                # In case tracking was not active and duration is 0
                # (i.e. new entry), start tracking, optionally stopping
                # current one
                currently_timetracked = line.get_currently_timetracked()
                currently_timetracked._stop_timetracking(now)
                affected_lines.extend(currently_timetracked)
                line._start_timetracking(now)
                affected_lines.append(line)
            else:
                # Otherwise make a copy and start tracking it,
                # optionally stopping current one
                currently_timetracked = line.get_currently_timetracked()
                currently_timetracked._stop_timetracking(now)
                affected_lines.extend(currently_timetracked)
                new_timetracked_line = line.copy({
                    'timetracker_started_at': None,
                    'timetracker_stopped_at': None,
                    'unit_amount': 0,
                })
                new_timetracked_line._start_timetracking(now)
                affected_lines.append(new_timetracked_line)

        return affected_lines

    @api.multi
    def action_timetracker(self):
        self.toggle_timetracker()

        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def action_refresh_timetracker(self):  # pragma: no cover
        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.multi
    def action_reset_timetracked_duration(self):
        self.reset_timetracked_duration()

        return {
            'type': 'ir.actions.act_view_reload',
        }

    @api.model
    @api.returns('self')
    def get_currently_timetracked(self, users=None):
        users = users or self.user_id or self.env.user
        return self.search([
            ('user_id', 'in', users.ids),
            ('timetracker_started_at', '!=', False),
            ('timetracker_stopped_at', '=', False),
        ])

    @api.multi
    def reset_timetracked_duration(self):
        for line in self.filtered('is_timetracked'):
            line.write({
                'unit_amount': line._calculate_duration(),
            })

    @api.multi
    def write(self, values):
        has_timetracker_started_at = 'timetracker_started_at' in values
        timetracker_started_at = values.get('timetracker_started_at')
        if timetracker_started_at:
            timetracker_started_at = fields.Datetime.to_datetime(
                timetracker_started_at
            )
        has_timetracker_stopped_at = 'timetracker_stopped_at' in values
        timetracker_stopped_at = values.get('timetracker_stopped_at')
        if timetracker_stopped_at:
            timetracker_stopped_at = fields.Datetime.to_datetime(
                timetracker_stopped_at
            )
        timetracker_started_at_unset = has_timetracker_started_at and \
            not timetracker_started_at
        timetracker_stopped_at_unset = has_timetracker_stopped_at and \
            not timetracker_stopped_at
        untimetracked = timetracker_started_at_unset and \
            timetracker_stopped_at_unset

        if timetracker_started_at and not timetracker_stopped_at and \
                self.filtered(lambda x: x.is_timetracker_running) and \
                self.filtered(lambda x: (
                    x.timetracker_started_at != timetracker_started_at)):
            raise ValidationError(_(
                'You can not alter Started At timestamp while timetracker is'
                ' active.'
            ))

        if 'date' in values and not untimetracked and \
                self.filtered(lambda x: x.is_timetracked):
            date = fields.Date.to_date(values['date'])
            if self.filtered(lambda x: x.date != date):
                raise ValidationError(_(
                    'You can not manually alter date of an entry tracked by'
                    ' timetracker.'
                ))

        if 'unit_amount' in values and values['unit_amount'] > 0.0 and \
                (not untimetracked or not timetracker_stopped_at) and \
                self.filtered(lambda x: x.is_timetracker_running):
            unit_amount = float(values['unit_amount'])
            if self.filtered(lambda x: x.unit_amount != unit_amount):
                raise ValidationError(_(
                    'You can not manually alter duration of an entry while'
                    ' timetracker is active.'
                ))

        return super().write(values)

    def _timesheet_preprocess(self, values):
        values = super()._timesheet_preprocess(values)

        timetracker_started_at = values.get('timetracker_started_at')
        timetracker_stopped_at = values.get('timetracker_stopped_at')

        if timetracker_started_at:
            values['date'] = fields.Datetime.to_datetime(
                timetracker_started_at
            ).date()

        if timetracker_started_at or timetracker_stopped_at and \
                'unit_amount' in values:
            values.pop('unit_amount', None)

        return values

    @api.multi
    def _timesheet_postprocess_values(self, values):
        result = super()._timesheet_postprocess_values(values)

        has_timetracker_started_at = 'timetracker_started_at' in values
        has_timetracker_stopped_at = 'timetracker_stopped_at' in values
        has_unit_amount = 'unit_amount' in values
        unit_amount = values.get('unit_amount')

        if any([x in values for x in self._unit_amount_depencencies()]):
            for line in self.filtered(
                    lambda x: x.project_id and x.is_timetracked):
                computed_unit_amount = line._calculate_duration()
                if has_unit_amount and \
                        not has_timetracker_started_at and \
                        not has_timetracker_stopped_at:
                    if float_compare(
                        unit_amount,
                        computed_unit_amount,
                        precision_rounding=(
                            line.product_uom_id.rounding
                        ),
                    ) != 0:
                        result[line.id].update({
                            'timetracker_stopped_at': (
                                line._timetracker_stopped_at_for(
                                    unit_amount
                                )
                            ),
                        })
                    elif unit_amount != computed_unit_amount:
                        result[line.id].update({
                            'unit_amount': computed_unit_amount,
                        })
                elif not has_unit_amount:
                    result[line.id].update({
                        'unit_amount': computed_unit_amount,
                    })

        return result

    def _unit_amount_depencencies(self):
        return [
            'timetracker_started_at',
            'timetracker_stopped_at',
            'project_id',
            'unit_amount',
        ]

    @api.multi
    def _timetracker_started_at_rounded(self):
        self.ensure_one()
        uom_hour = self.env.ref('uom.product_uom_hour')

        timetracker_started_at = self.timetracker_started_at
        if self.project_id.timetracker_rounding_enabled and \
                self.project_id.timetracker_started_at_rounding:
            start_base = (
                timetracker_started_at - timedelta(days=1)
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            start_offset = uom_hour._compute_quantity(
                (timetracker_started_at - start_base) / timedelta(hours=1),
                self.product_uom_id,
                round=(
                    self.project_id.timetracker_rounding_enabled and
                    self.project_id.timetracker_started_at_rounding
                ),
                rounding_method=(
                    self.project_id.timetracker_started_at_rounding
                ),
            )
            timetracker_started_at = start_base + timedelta(hours=(
                self.product_uom_id._compute_quantity(
                    start_offset,
                    uom_hour,
                    round=(
                        self.project_id.timetracker_rounding_enabled and
                        self.project_id.timetracker_started_at_rounding
                    ),
                    rounding_method=(
                        self.project_id.timetracker_started_at_rounding
                    ),
                )
            ))
            _logger.debug(
                'Start %s rounded to %s (start_offset = %s, base = %s)',
                self.timetracker_started_at,
                timetracker_started_at,
                start_offset,
                start_base
            )

        return timetracker_started_at

    @api.multi
    def _timetracker_stopped_at_for(self, unit_amount):
        self.ensure_one()
        duration = self.product_uom_id._compute_quantity(
            unit_amount,
            self.env.ref('uom.product_uom_hour'),
        )
        timetracker_stopped_at = (
            self._timetracker_started_at_rounded() + timedelta(
                hours=duration
            )
        )

        return max(
            self.timetracker_started_at,
            timetracker_stopped_at
        )

    @api.multi
    def _timetracker_stopped_at_rounded(self):
        self.ensure_one()
        uom_hour = self.env.ref('uom.product_uom_hour')

        timetracker_stopped_at = self.timetracker_stopped_at
        if self.project_id.timetracker_rounding_enabled and \
                self.project_id.timetracker_stopped_at_rounding:
            stop_base = (
                timetracker_stopped_at - timedelta(days=1)
            ).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            stop_offset = uom_hour._compute_quantity(
                (timetracker_stopped_at - stop_base) / timedelta(hours=1),
                self.product_uom_id,
                round=True,
                rounding_method=(
                    self.project_id.timetracker_stopped_at_rounding
                ),
            )
            timetracker_stopped_at = stop_base + timedelta(hours=(
                self.product_uom_id._compute_quantity(
                    stop_offset,
                    uom_hour,
                    round=True,
                    rounding_method=(
                        self.project_id.timetracker_stopped_at_rounding
                    ),
                )
            ))
            _logger.debug(
                'Stop %s rounded to %s (stop offset = %s, base = %s)',
                self.timetracker_stopped_at,
                timetracker_stopped_at,
                stop_offset,
                stop_base
            )

        return timetracker_stopped_at

    @api.multi
    def _calculate_duration(self):
        self.ensure_one()
        if not self.timetracker_started_at or \
                not self.timetracker_stopped_at:
            return 0

        timetracker_started_at = self._timetracker_started_at_rounded()
        timetracker_stopped_at = self._timetracker_stopped_at_rounded()

        if timetracker_stopped_at < timetracker_started_at:
            return 0.0

        uom_hour = self.env.ref('uom.product_uom_hour')

        return uom_hour._compute_quantity(
            (
                timetracker_stopped_at - timetracker_started_at
            ) / timedelta(hours=1),
            self.product_uom_id
        )
