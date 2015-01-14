# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc


class hr_timesheet_sheet(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet"

    _columns = {
        'validator_user_ids': fields.many2many('res.users', string='Validators',
                                               required=False),
    }

    def _default_department(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        emp_ids = emp_obj.search(cr, uid, [('user_id', '=', uid)],
                                 context=context)
        emps = emp_obj.browse(cr, uid, emp_ids, context=context)

        for emp in emps:
            return emp.department_id and emp.department_id.id or False
        return False

    _defaults = {
        'department_id': _default_department,
    }

    def _get_validator_user_ids(self, cr, uid, ids, context=None):
        res = {}
        users = {}
        for timesheet in self.browse(cr, uid, ids):
            res[timesheet.id] = []
            users[timesheet.id] = []
            if timesheet.employee_id \
                    and timesheet.employee_id.parent_id \
                    and timesheet.employee_id.parent_id.user_id:
                users[timesheet.id].append(
                    timesheet.employee_id.parent_id.user_id.id)
            if timesheet.department_id \
                    and timesheet.department_id.manager_id \
                    and timesheet.department_id.manager_id.user_id \
                    and timesheet.department_id.manager_id.user_id.id != uid:
                users[timesheet.id].append(
                    timesheet.department_id.manager_id.user_id.id)
            elif timesheet.department_id \
                    and timesheet.department_id.parent_id \
                    and timesheet.department_id.parent_id.manager_id \
                    and timesheet.department_id.parent_id.manager_id.user_id \
                    and timesheet.department_id.parent_id.\
                    manager_id.user_id.id != uid:
                users[timesheet.id].append(
                    timesheet.department_id.manager_id.user_id.id)


            [res[timesheet.id].append(item) for item in users[timesheet.id]
             if item not in res[timesheet.id]]
        return res

    def button_confirm(self, cr, uid, ids, context=None):
        validators = self._get_validator_user_ids(cr, uid,
                                                  ids, context=context)
        for sheet in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, sheet.id,
                       {'validator_user_ids':
                           [(4, user_id) for user_id
                            in validators[sheet.id]]})
        return super(hr_timesheet_sheet, self).button_confirm(cr, uid, ids,
                                                              context=context)

    def _check_authorised_validator(self, cr, uid, ids, *args):
        model_data_obj = self.pool.get('ir.model.data')
        res_groups_obj = self.pool.get("res.groups")
        group_hr_manager_id = model_data_obj._get_id(
            cr, uid, 'base', 'group_hr_manager')
        group_hr_user_id = model_data_obj._get_id(
            cr, uid, 'base', 'group_hr_user')

        for timesheet in self.browse(cr, uid, ids):
            if group_hr_manager_id:
                    res_id = model_data_obj.read(cr, uid, [group_hr_manager_id],
                                                 ['res_id'])[0]['res_id']
                    group_hr_manager = res_groups_obj.browse(
                        cr, uid, res_id)
                    group_hr_manager_ids = [user.id for user
                                            in group_hr_manager.users]
                    if uid in group_hr_manager_ids:
                        continue

            if group_hr_user_id:
                    res_id = model_data_obj.read(cr, uid, [group_hr_user_id],
                                                 ['res_id'])[0]['res_id']
                    group_hr_user = res_groups_obj.browse(
                        cr, uid, res_id)
                    group_hr_user_ids = [user.id for user
                                         in group_hr_user.users]
                    if uid in group_hr_user_ids:
                        continue

            validator_user_ids = []
            for validator_user_id in timesheet.validator_user_ids:
                validator_user_ids.append(validator_user_id.id)
            if uid not in validator_user_ids:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('You are not authorised to approve'
                                       ' or refuse this Timesheet.'))

    def action_set_to_draft(self, cr, uid, ids, *args):
        self._check_authorised_validator(cr, uid, ids, *args)
        return super(hr_timesheet_sheet, self).action_set_to_draft(
            cr, uid, ids, *args)

    def action_done(self, cr, uid, ids, *args):
        self._check_authorised_validator(cr, uid, ids, *args)
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_validate(uid, 'hr_timesheet_sheet.sheet',
                                    id, 'done', cr)
        return True

    def action_cancel(self, cr, uid, ids, *args):
        self._check_authorised_validator(cr, uid, ids, *args)
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_validate(uid, 'hr_timesheet_sheet.sheet',
                                    id, 'cancel', cr)
        return True
