# -*- coding: utf-8 -*-
# Copyright 2015 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2017 Martronic SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
    _order = 'date desc, time_start desc, time_stop desc, id desc'

    time_start = fields.Float(string='Begin Hour')
    time_stop = fields.Float(string='End Hour')

    @api.multi
    @api.constrains('time_start', 'time_stop', 'unit_amount')
    def _check_time_start_stop(self):
        self.ensure_one()
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

    @api.onchange('time_start', 'time_stop')
    def onchange_hours_start_stop(self):
        start = timedelta(hours=self.time_start)
        stop = timedelta(hours=self.time_stop)
        if stop < start:
            return
        self.unit_amount = (stop - start).seconds / 3600
