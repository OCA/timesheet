# -*- coding: utf-8 -*-
##############################################################################
#
#    Author : Yannick Vaucher (Camptocamp)
#    Copyright 2013 Camptocamp SA
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
##############################################################################
from openerp import models, fields


class HrAnalyticTimesheet(models.Model):
    """Set order by line date and analytic account name instead of id
    We create related stored values as _order cannot be used on inherited
    columns.
    """
    _inherit = "hr.analytic.timesheet"
    _order = "date_aal DESC, account_name ASC"

    date_aal = fields.Date(related='line_id.date',
                           store=True, readonly=True)

    account_name = fields.Char(related='account_id.name',
                               store=True, readonly=True)

    def _register_hook(self, cr):
        """Patch recomputation of sheet_id to never recompute when
        account_name changes"""
        if self._columns['sheet_id'].store.get(
                'hr.analytic.timesheet', [None, None, None]
        )[1] is None:
            trigger = self._columns['sheet_id'].store['hr.analytic.timesheet']
            self._columns['sheet_id'].store['hr.analytic.timesheet'] = (
                trigger[0],
                [f for f in self._columns.keys() if f != 'account_name'],
                trigger[2],
            )
        return super(HrAnalyticTimesheet, self)._register_hook(cr)
