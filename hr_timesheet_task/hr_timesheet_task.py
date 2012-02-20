# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time

import netsvc
from osv import fields
from osv import osv
import decimal_precision as dp
from tools.translate import _


####################################################################################
#  HR Timesheet analytic
####################################################################################
class hr_analytic_timesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"
    ALLOWED_FIELD = ('name','to_invoice','task_id','invoice_id','account_id')
    
    def _check(self, cr, uid, ids, *args, **kwargs):
        """Used by the unlink method to allow the deletion on unconfirmed TS."""
        return super(hr_analytic_timesheet,self)._check(cr, uid, ids,*args, **kwargs)
        
    def _check_date_validity(self, cr, uid, att, vals, context=None):
        context = context or {}
        if 'date' in vals:
            ts = self.pool.get('hr_timesheet_sheet.sheet')
            date = vals['date']
            ids2 = ts.search(cr, 
                             uid, 
                             [('user_id', '=', att.user_id.id),
                              ('date_from', '<=', date),
                              ('date_to', '>=', date),
                              ('state', 'in', ['confirm','done'])],
                             context=context)
            if ids2:
                raise osv.except_osv(_('Error !'), 
                                     _('You can not change the date for' 
                                       ' the Confirmed/Done timesheet line %s!') % (att.name,))
        
    def _check_authorized_field(self, cr, uid, ids, vals, context=None):
        """Raise an error if the field are not in the dict of allowed
        field when TS is confirmed. Used in the write method to allow project manager
        to change some values."""
        # Check if we have other fields than allowed ones
        context = context or {}
        if set(vals.keys()).issubset(self.ALLOWED_FIELD):
            for att in self.browse(cr, uid, ids):
                if att.sheet_id and att.sheet_id.state not in ('draft', 'new'):
                    raise osv.except_osv(_('Error !'), 
                                         _("Only the following field can be modified"
                                           " on a confirmed timesheet : %s !" ) % (str(self.ALLOWED_FIELD)))
                self._check_date_validity(cr, uid, att, vals, context=context)
        
        return True
    
    def _check_sheet_state(self, cr, uid, ids, context=None):
        """We want project manager to be able to change some value when TS is confirmed.
        So This constraint return always True, and we'll check that in unlink, write and create method
        instead."""
        return True

    def _check_creation_allowed(self, cr, uid, vals, context=None):
        """Check if we try to create a line on a confirmed timesheet, and if it is the case,
        raise an error."""
        ts = self.pool.get('hr_timesheet_sheet.sheet')
        if context is None:
            context = {}
        date = vals['date']
        user = vals['user_id']
        ids = ts.search(cr, 
                        uid, 
                        [('user_id','=',user),
                         ('date_from','<=',date),
                         ('date_to','>=',date),
                         ('state','in',['confirm','done'])],
                        context=context)
        if ids:
            raise osv.except_osv(_('Error !'),
                                 _('You can not create an entry in a Confirmed/Done timesheet !'))
        return True
        
    _constraints = [
        (_check_sheet_state, 'You can not modify an entry in a Confirmed/Done timesheet !', ['state']),
    ]
    
    # Infos mapping with project_task_work :
        # Taks Work             Hr analytic TS      Comments
        # 'name':               name
        # 'date':               date
        # 'hours':              unit_amount         Warning, here in a specific UoM
        # 'user_id':            user_id
        # 'company_id':         company_id

    _columns={
        'task_id':fields.many2one('project.task','Task', ondelete='set null'),
        # This field will always be computed regarding the project default UoM info's
        # I don't make a function field because OpenERP SA didn't do it in project timesheet
        # module, so I keep the same philosophy (but IMHO it is not good...).
        # 'hours': fields.float('Time Spent', readonly=True),
    }

    def on_change_unit_amount(self, cr, uid, id, prod_id, unit_amount, company_id, 
                              unit=False, journal_id=False, task_id=False, 
                              to_invoice=False, context=None):
        res = super(hr_analytic_timesheet, self).on_change_unit_amount(cr, uid, id, prod_id, 
                                                                       unit_amount, company_id,
                                                                       unit, journal_id, context)
        if 'value' in res and task_id:
            aa = self.pool.get('project.task').browse(cr, uid, task_id).project_id.analytic_account_id
            res['value']['account_id'] = aa.id
            if aa.to_invoice and not to_invoice:
                res['value']['to_invoice'] = aa.to_invoice.id
        return res
    
    def on_change_account_id(self, cr, uid, ids, account_id,context=None):
        """If project has only one open task, we choose it ! """
        # TODO: Could be improved for the user, for
        # example, we can make something like : if user has already made timesheet lines on a task
        # we suggest this one
        res = super(hr_analytic_timesheet,self).on_change_account_id(cr,uid,ids,account_id)
        if account_id:
            task_obj = self.pool.get('project.task')
            proj_obj = self.pool.get('project.project')
            proj_ids = proj_obj.search(cr,uid,[('analytic_account_id','=', account_id)])
            if not proj_ids:
                return res
            task_ids = task_obj.search(cr,uid,[('project_id', '=', proj_ids[0]),('state', '=', 'open')])
            if len(task_ids) == 1:
                res['value']['task_id'] = task_ids[0]
        return res

    # I'm not sure about this way to do this, but OpenERP SA do it this way for project_timesheet
    # so I keep the same philosophy
    def create(self, cr, uid, vals, *args, **kwargs):
        context = kwargs.get('context', {})
        self._check_creation_allowed(cr, uid, vals, context)
        task_pool = self.pool.get('project.task')
        res = super(hr_analytic_timesheet,self).create(cr, uid, vals, *args, **kwargs)
        hr_ts_line = self.browse(cr,uid,res)
        # If possible update the remaining hours in related task
        if 'task_id' in vals and vals['task_id']:
            task_remaining_hours = task_pool.read(cr,
                                                  uid,
                                                  vals['task_id'],
                                                  ['remaining_hours'],
                                                  context=context)['remaining_hours']
            task_pool.write(cr, uid,
                            vals['task_id'],
                            {'remaining_hours': task_remaining_hours - hr_ts_line.hours_to_inv},
                            context=context)
        return 

    def _onwrite_manage_proj_indicators(self, cr, uid, ids, vals, context=None):
        """Manage and write the needed value for all projects/tasks indicators. We'll
        use it also in aal."""
        context = context or {}
        old_vals = context.get('old_vals', {})
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        self._check_authorized_field(cr, uid, ids, vals)
        task_pool = self.pool.get('project.task')
        aal_obj = self.pool.get('account.analytic.line')
        for line in self.browse(cr, uid, ids, context=context):
            # take the new value and compute with factor
            unit_amount = vals.get('unit_amount', line.unit_amount)
            uom = vals.get('product_uom_id', line.product_uom_id.id)
            to_invoice_id = vals.get('to_invoice', line.to_invoice.id)
            amount_project_uom = aal_obj._compute_proj_unit(cr, uid, uom, unit_amount)
            new_value = aal_obj._compute_hours_factor_from_inv(cr, uid, amount_project_uom, to_invoice_id)
            old_value = line.hours_to_inv or 0.0
            # If task id exists => update the remaining_hours fields of the related task
            old_task_to_compute = new_task_to_compute = False
            # amount_difference = new_value - old_value
            # Add a new task on existing line
            old_task =  old_vals.get(line.id, {}).get('task_id', False)
            if not old_task and line.task_id: #we add a new task
                new_task_to_compute = line.task_id
            elif old_task and line.task_id: #we change task
                new_task_to_compute = line.task_id
                old_task_to_compute =  task_pool.browse(cr, uid, old_task)
            elif old_task and not line.task_id: #we set task to null
                old_task_to_compute = task_pool.browse(cr, uid, old_task)
            elif line.id in old_vals and not old_task: #use if write is triggered from 
                # In that particular case, new_value is equal to the difference
                # We doesn't change task, but unit_amount or uom
                new_task_to_compute = line.task_id
                new_value = new_value - old_value
                
            if new_task_to_compute:
                task_pool.write(cr, uid, new_task_to_compute.id,
                                {'remaining_hours': new_task_to_compute.remaining_hours - new_value},
                                context=context)
            if old_task_to_compute:
                task_pool.write(cr, uid, old_task_to_compute.id,
                                {'remaining_hours': old_task_to_compute.remaining_hours + old_value},
                                context=context)
            
            # To ensure 'hours' field is written from AAL
            if context.get('active_model', False) != 'hr.analytic.timesheet':
                context['stop_write'] = True
        # return vals['hours']
        return True

    def write(self, cr, uid, ids, vals, context=None):
        # Keep old recorded values
        old_vals={}
        if isinstance(ids, (int, long)):
            ids = [ids]
        for ts_line in self.browse(cr, uid, ids):
            old_vals[ts_line.id] = {}
            # We have an old value, different from the new one
            if vals.get('task_id'):
                if ts_line.task_id and (ts_line.task_id.id != vals['task_id']):
                    old_vals[ts_line.id] = {'task_id' : ts_line.task_id.id}
        context['old_vals'] = old_vals
        return super(hr_analytic_timesheet, self).write(cr, uid, ids, vals, context=context)

    def _onunlink_manage_proj_indicators(self,cr,uid,ids,context):
        """Manage and write the needed value for all projects/tasks indicators. We'll
        use it also in aal."""
        if isinstance(ids, (int, long)):
            ids = [ids]
        self._check(cr, uid, ids)
        task_pool = self.pool.get('project.task')
        for line in self.browse(cr, uid, ids):
            if line.task_id:
                # new_value = self._compute_proj_unit(cr,uid,line.product_uom_id.id,line.unit_amount)
                task_pool.write(cr, uid, line.task_id.id,
                                {'remaining_hours': line.task_id.remaining_hours + line.hours_to_inv},
                                context=context)
        return True

hr_analytic_timesheet()

