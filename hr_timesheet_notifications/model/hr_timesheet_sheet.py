# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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

from openerp.osv import orm


class HrTimesheetSheet(orm.Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    def create(self, cr, uid, vals, context=None):
        """
        Subscribe the manager to their users' sheets
        """
        sheet_id = super(HrTimesheetSheet, self).create(
            cr, uid, vals, context=context)
        sheet = self.browse(cr, uid, sheet_id, context=context)

        # Subscribe the manager to comments and sheet confirmation
        data_obj = self.pool['ir.model.data']
        subtype_ids = [
            data_obj.get_object_reference(cr, uid, 'mail', 'mt_comment')[1],
            data_obj.get_object_reference(
                cr, uid, 'hr_timesheet_notifications', 'subtype_confirm')[1],
            ]

        if sheet.employee_id.parent_id.user_id:
            sheet.message_subscribe_users(
                subtype_ids=subtype_ids,
                user_ids=[sheet.employee_id.parent_id.user_id.id])
        return sheet_id

    _track = {
        'state': {
            'hr_timesheet_notifications.subtype_draft': (
                lambda self, cr, uid, obj, context=None:
                obj['state'] == 'draft'),
            'hr_timesheet_notifications.subtype_confirm': (
                lambda self, cr, uid, obj, context=None:
                obj['state'] == 'confirm'),
            'hr_timesheet_notifications.subtype_done': (
                lambda self, cr, uid, obj, context=None:
                obj['state'] == 'done'),
            },
        }
