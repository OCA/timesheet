# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Yannick Vaucher (Camptocamp)
#             Vincent Renaville (Camptocamp)
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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrAttendance(orm.Model):
    """Alter the default date for manual setting"""
    _inherit = "hr.attendance"

    def _default_date(self, cr, uid, context=None):
        sheet_id = context.get('sheet_id')
        if not sheet_id:
            return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        ts_obj = self.pool.get('hr_timesheet_sheet.sheet')
        timesheet = ts_obj.browse(cr, uid, sheet_id, context=context)
        dates = [a.name for a in timesheet.attendances_ids]
        if not dates:
            return timesheet.date_from
        return max(dates)

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
        # Check sign in signout in the same timesheet only
        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        for att in self.browse(cr, uid, ids, context=context):
            sheet_id = sheet_obj.search(
                cr, uid, [
                    ('employee_id', '=', att.employee_id.id),
                    ('date_from', '<=', att.name),
                    ('date_to', '>=', att.name),
                ],
                limit=1,
                context=context)
            sheet_id = sheet_id and sheet_id[0] or False

            # search and browse for first previous and first next records
            prev_att_ids = self.search(
                cr, uid, [('employee_id', '=', att.employee_id.id),
                          ('sheet_id', '=', sheet_id),
                          ('name', '<', att.name),
                          ('action', 'in', ('sign_in', 'sign_out'))],
                limit=1, order='name DESC', context=context)
            next_add_ids = self.search(
                cr, uid, [('employee_id', '=', att.employee_id.id),
                          ('sheet_id', '=', sheet_id),
                          ('name', '>', att.name),
                          ('action', 'in', ('sign_in', 'sign_out'))],
                limit=1, order='name ASC', context=context)
            prev_atts = self.browse(cr, uid, prev_att_ids, context=context)
            next_atts = self.browse(cr, uid, next_add_ids, context=context)
            # check for alternance, return False if at least one condition is
            # not satisfied
            # previous exists and is same action
            if prev_atts and prev_atts[0].action == att.action:
                return False
            # next exists and is same action
            if next_atts and next_atts[0].action == att.action:
                return False
            # first attendance must be sign_in
            if (not prev_atts) and (not next_atts) and att.action != 'sign_in':
                return False
        return True

    _constraints = [
        (_altern_si_so,
         'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign '
         'in)', ['action'])]

    _defaults = {
        'name': _default_date,
    }
