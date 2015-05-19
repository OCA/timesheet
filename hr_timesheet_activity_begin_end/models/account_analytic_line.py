# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from __future__ import division

import math
from datetime import timedelta

from openerp import models, fields, api, exceptions, _
from openerp.tools.float_utils import float_compare


def float_time_convert(float_val):
    hours = math.floor(abs(float_val))
    mins = abs(float_val) - hours
    mins = round(mins * 60)
    if mins >= 60.0:
        hours = hours + 1
        mins = 0.0
    return '%02d:%02d' % (hours, mins)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    time_start = fields.Float(string='Begin Hour')
    time_stop = fields.Float(string='End Hour')

    @api.one
    @api.constrains('time_start', 'time_stop', 'unit_amount')
    def _check_time_start_stop(self):
        start = timedelta(hours=self.time_start)
        stop = timedelta(hours=self.time_stop)
        if stop < start:
            raise exceptions.ValidationError(
                _('The beginning hour (%s) must '
                  'precede the ending hour (%s).') %
                (float_time_convert(self.time_start),
                 float_time_convert(self.time_stop))
            )
        hours = (stop - start).seconds / 3600
        if (hours and
                float_compare(hours, self.unit_amount, precision_digits=4)):
            raise exceptions.ValidationError(
                _('The duration (%s) must be equal to the difference '
                  'between the hours (%s).') %
                (float_time_convert(self.unit_amount),
                 float_time_convert(hours))
            )
        # check if lines overlap
        others = self.search([
            ('id', '!=', self.id),
            ('user_id', '=', self.user_id.id),
            ('date', '=', self.date),
            ('time_start', '<', self.time_stop),
            ('time_stop', '>', self.time_start),
        ])
        if others:
            message = _("Lines can't overlap:\n")
            message += '\n'.join(['%s - %s' %
                                  (float_time_convert(line.time_start),
                                   float_time_convert(line.time_stop))
                                  for line
                                  in (self + others).sorted(
                                      lambda l: l.time_start
                                  )])
            raise exceptions.ValidationError(message)


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    _order = "id desc"
    _order = ("aal_date DESC, aal_time_start DESC,"
              "aal_time_stop DESC, aal_account_name ASC")

    aal_date = fields.Date(
        string='Analytic Line Date',
        related='line_id.date',
        store=True,
        readonly=True,
    )
    aal_time_start = fields.Float(
        string='Analytic Line Begin Hour',
        related='line_id.time_start',
        store=True,
        readonly=True,
    )
    aal_time_stop = fields.Float(
        string='Analytic Line Begin Hour',
        related='line_id.time_stop',
        store=True,
        readonly=True,
    )
    aal_account_name = fields.Char(
        string='Analytic Account Name',
        related='account_id.name',
        store=True,
        readonly=True,
    )

    @api.onchange('time_start', 'time_stop')
    def onchange_hours_start_stop(self):
        start = timedelta(hours=self.time_start)
        stop = timedelta(hours=self.time_stop)
        if stop < start:
            return
        self.unit_amount = (stop - start).seconds / 3600
