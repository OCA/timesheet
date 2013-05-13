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
import time

from openerp.osv import orm


class HrAttendance(orm.Model):
    """
    Alter the default date for manual setting
    """
    _inherit = "hr.attendance"

    def _default_date(self, cr, uid, context=None):
        sheet_id = context.get('sheet_id')
        if not sheet_id:
            return time.strftime('%Y-%m-%d %H:%M:%S')

        ts_obj = self.pool.get('hr_timesheet_sheet.sheet')
        timesheet = ts_obj.browse(cr, uid, sheet_id, context=context)

        dates = [a.name for a in timesheet.attendances_ids]

        if not dates:
            return timesheet.date_from

        return max(dates)


    _defaults = {
        'name': _default_date,
        }

