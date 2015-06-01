# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
from openerp.osv.orm import Model
from openerp.osv import fields


class HrTimesheetSheet(Model):
    _inherit = 'hr_timesheet_sheet.sheet'

    _columns = {
        'done_uid': fields.many2one('res.users', string='Approved by',
                                    readonly=True),
    }

    def write(self, cr, uid, ids, vals, context=None):

        if 'state' in vals:
            if vals['state'] == 'done':
                vals['done_uid'] = uid
            else:
                vals['done_uid'] = False

        return super(HrTimesheetSheet, self).write(cr, uid, ids, vals,
                                                   context=context)
