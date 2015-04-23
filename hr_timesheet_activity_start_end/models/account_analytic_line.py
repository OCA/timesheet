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

from datetime import timedelta

from openerp import models, fields, api, exceptions, _
from openerp.tools.float_utils import float_compare


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    hour_start = fields.Float(string='Begin Hour')
    hour_stop = fields.Float(string='End Hour')

    @api.one
    @api.constrains('hour_start', 'hour_stop', 'unit_amount')
    def _check_hour_start_stop(self):
        start = timedelta(hours=self.hour_start)
        stop = timedelta(hours=self.hour_stop)
        if stop < start:
            raise exceptions.ValidationError(
                _('The start hour must precede the end hour.')
            )
        hours = (stop - start).seconds / 3600
        if (hours and
                float_compare(hours, self.unit_amount, precision_digits=4)):
            raise exceptions.ValidationError(
                _('The duration must be equal to the difference '
                  'between the hours.')
            )


class HrAnalyticTimesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    @api.onchange('hour_start', 'hour_stop')
    def onchange_hours_start_stop(self):
        start = timedelta(hours=self.hour_start)
        stop = timedelta(hours=self.hour_stop)
        if stop < start:
            return
        self.unit_amount = (stop - start).seconds / 3600
