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
        
    def _check_authorized_field(self, cr, uid, ids, vals,context=None):
        """Raise an error if the field are not in the dict of allowed
        field when TS is confirmed. Used in the write method to allow project manager
        to change some values."""
        # Check if we have other fields than allowed ones
        if len(set(vals).difference(self.ALLOWED_FIELD)):
        # if len(set(self.ALLOWED_FIELD).intersection(vals)) > len(vals) or :
            # If yes, then check the TS state => if confirmed, raise an error
            for att in self.browse(cr, uid, ids):
                if att.sheet_id and att.sheet_id.state not in ('draft', 'new'):
                    raise osv.except_osv(_('Error !'), _("Only the following field can be modified on a confirmed timesheet : %s !"%(str(self.ALLOWED_FIELD))))
        # If we change the date, check that the new TS isn't confirm
        if 'date' in vals:
            ts = self.pool.get('hr_timesheet_sheet.sheet')
            if context is None:
                context = {}
            date = vals['date']
            users=[]
            # For all concerned user:
            for inst in self.browse(cr,uid,ids):
                users.append(inst.user_id.id)
            ids2 = ts.search(cr, uid, [('user_id','in',users),('date_from','<=',date), ('date_to','>=',date), ('state','in',['confirm','done'])], context=context)
            if ids2:
                raise osv.except_osv(_('Error !'), _('You can not change the date for a Confirmed/Done timesheet !'))
        
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
        ids = ts.search(cr, uid, [('user_id','=',user),('date_from','<=',date), ('date_to','>=',date), ('state','in',['confirm','done'])], context=context)
        if ids:
            raise osv.except_osv(_('Error !'), _('You can not create an entry in a Confirmed/Done timesheet !'))
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
    def _compute_proj_unit(self, cr, uid, product_uom_id, unit_amount, context=None):
        """Compute the unit_amount entred by the user in project default unit if not the same.
        Store the value in 'hours' field like it was before with project_task_work"""
        default_uom = self.pool.get('res.users').browse(cr, uid, uid).company_id.project_time_mode_id.id
        uom_obj = self.pool.get('product.uom')
        res = 0.00
        if product_uom_id != default_uom:
            res = uom_obj._compute_qty(cr, uid, product_uom_id, unit_amount, default_uom)
        else:
            res = unit_amount
        return res

    _columns={
        'task_id':fields.many2one('project.task','Task', ondelete='set null'),
        # This field will always be computed regarding the project default UoM info's
        # I don't make a function field because OpenERP SA didn't do it in project timesheet
        # module, so I keep the same philosophy (but IMHO it is not good...).
        'hours': fields.float('Time Spent', readonly=True),
    }

    def on_change_unit_amount(self, cr, uid, id, prod_id, unit_amount, company_id, unit=False, journal_id=False, task_id=False,context=None):
        res = super(hr_analytic_timesheet,self).on_change_unit_amount(cr, uid, id, prod_id, unit_amount, company_id, unit, journal_id, context)
        if 'value' in res and task_id:
            aa = self.pool.get('project.task').browse(cr,uid,task_id).project_id.analytic_account_id
            res['value']['account_id'] = aa.id
            if aa.to_invoice:
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
            proj_ids = proj_obj.search(cr,uid,[('analytic_account_id','=',account_id)])
            task_ids = task_obj.search(cr,uid,[('project_id','=',proj_ids),('state','=','open')])
            if len(task_ids) == 1:
                res['value']['task_id'] = task_ids[0]
        return res

    # I'm not sure about this way to do this, but OpenERP SA do it this way for project_timesheet
    # so I keep the same philosophy
    def create(self, cr, uid, vals, *args, **kwargs):
        self._check_creation_allowed(cr, uid, vals, context=None)
        context = kwargs.get('context', {})
        task_pool = self.pool.get('project.task')
        value = 0.0
        if 'unit_amount' in vals and (not vals['unit_amount']):
            vals['unit_amount'] = 0.00
        # In any possible case update the hours vals
        if 'product_uom_id' in vals and vals['product_uom_id'] and 'unit_amount' in vals:
            # We need to update the work done and the hours field
            value = self._compute_proj_unit(cr,uid,vals['product_uom_id'],vals['unit_amount'])
            vals['hours'] = value
        # If possible update the remaining hours in related task
        if 'task_id' in vals and vals['task_id']:
            task_remaining_hours = task_pool.read(cr, uid, vals['task_id'],
                                                  ['remaining_hours'],
                                                  context=context)['remaining_hours']
            task_pool.write(cr, uid,
                            vals['task_id'],
                            {'remaining_hours': task_remaining_hours - value},
                            context=context)
        return super(hr_analytic_timesheet,self).create(cr, uid, vals, *args, **kwargs)

    def _onwrite_manage_proj_indicators(self,cr,uid,ids,vals,context=None):
        """Manage and write the needed value for all projects/tasks indicators. We'll
        use it also in aal."""
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        self._check_authorized_field(cr,uid,ids,vals)
        if 'unit_amount' in vals and (not vals['unit_amount']):
            vals['unit_amount'] = 0.00
        task_pool = self.pool.get('project.task')
        for line in self.browse(cr, uid, ids, context=context):
            # Re-compute hours field and write it
            unit_amount = vals.get('unit_amount', line.unit_amount)
            uom = vals.get('product_uom_id', line.product_uom_id.id)
            new_value = self._compute_proj_unit(cr, uid, uom, unit_amount)
            vals['hours'] = new_value
            # If task id exists => update the remaining_hours fields of the related task
            old_task = new_task = False
            amount_difference = 0.0
            # Add a new or modify a task on a line
            if vals.get('task_id',False) and vals['task_id']:
                new_task = task_pool.browse(cr,uid,vals['task_id'])
                old_task = line.task_id
                amount_difference = new_value
            # Set null on task_id
            elif 'task_id' in vals and not vals['task_id']:
                old_task = line.task_id
            # We doesn't change task, but unit_amount or uom
            elif line.task_id:
                new_task = line.task_id
                amount_difference = new_value - line.hours
            if new_task:
                task_pool.write(cr, uid, new_task.id,
                                {'remaining_hours': new_task.remaining_hours - amount_difference},
                                context=context)
            if old_task:
                task_pool.write(cr, uid, old_task.id,
                                {'remaining_hours': old_task.remaining_hours + line.hours},
                                context=context)
            
            # To ensure 'hours' field is written from AAL
            if context.get('active_model',False) != 'hr.analytic.timesheet':
                context['stop_write'] = True
                self.write(cr,uid,line.id,{'hours':new_value},context=context)
        return vals['hours']

    def write(self, cr, uid, ids, vals, context=None):
        if not context.get('stop_write',False):
            vals['hours'] = self._onwrite_manage_proj_indicators(cr,uid,ids,vals,context)            
        return super(hr_analytic_timesheet,self).write(cr, uid, ids, vals, context)

    def _onunlink_manage_proj_indicators(self,cr,uid,ids,*args,**kwargs):
        """Manage and write the needed value for all projects/tasks indicators. We'll
        use it also in aal."""
        if isinstance(ids, (int, long)):
            ids = [ids]
        self._check(cr, uid, ids)
        context = kwargs.get('context', {})
        task_pool = self.pool.get('project.task')
        for line in self.browse(cr, uid, ids):
            if line.task_id:
                new_value = self._compute_proj_unit(cr,uid,line.product_uom_id.id,line.unit_amount)
                task_pool.write(cr, uid, line.task_id.id,
                                {'remaining_hours': line.task_id.remaining_hours + new_value},
                                context=context)

    def unlink(self, cr, uid, ids, *args, **kwargs):
        self._onunlink_manage_proj_indicators(cr,uid,ids,*args,**kwargs)
        context = kwargs.get('context', {})
        context['preserve_aa_lines'] = True
        kwargs['context'] = context
        return super(hr_analytic_timesheet,self).unlink(cr, uid, ids,*args, **kwargs)

hr_analytic_timesheet()

