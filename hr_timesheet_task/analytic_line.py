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
#  Analytic Lines
####################################################################################
class analytic_account_line(osv.osv):
    """Override default write and unlink method to ensure the same check as
    done in hr.analytic.timesheet: we can only change some field on a confirmed TS +
    unlink can't be done if TS confirmed.
    Add a store field for hours spent with to_invoice factor.
    """

    _inherit = "account.analytic.line"

    def _compute_proj_unit(self, cr, uid, product_uom_id, unit_amount, context=None):
        """Compute the unit_amount entred by the user in project default unit if not the same.
        Store the value in 'hours' field like it was before with project_task_work. 
        """
        default_uom = self.pool.get('res.users').browse(cr, uid, uid).company_id.project_time_mode_id.id
        uom_obj = self.pool.get('product.uom')
        res = 0.00
        ##
        # We put the try/except bloc because if conversion is impossible, it means that we are not in a 
        # product have not an time uom , so we return 0.0
        ##
        try:
            if product_uom_id != default_uom:
                res = uom_obj._compute_qty(cr, uid, product_uom_id, unit_amount, default_uom)
            else:
                res = unit_amount
        except:
            res = 0.0
        return res

    def _check_inv(self, cr, uid, ids, vals):
        """We override this method cause we want to allow to change allowed field even when 
        invoiced."""
        select = ids
        hr_ts_obj=self.pool.get('hr.analytic.timesheet')
        if isinstance(select, (int, long)):
            select = [ids]
        if (not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(cr, uid, select):
                # If invoiced...
                if line.invoice_id:
                    # Check that there is a hr_ts line linked to this aal
                    get_hr_al_ids = self._get_hr_analytic_ids(cr, uid, ids)
                    if 'hral' in get_hr_al_ids and get_hr_al_ids['hral']:
                        # yes => _check_authorized_field
                        hr_ts_obj._check_authorized_field
                    else:
                    # No => Raise
                        raise osv.except_osv(_('Error !'),
                            _('You can not modify an invoiced analytic line!'))
        return True

    def _compute_hours_factor(self, hours, factor):
        if not factor:
            factor = 0.0
        return hours * ((100 - factor)/100)

    def _compute_hours_factor_from_inv(self, cr, uid, hours, to_invoice_id):
        """Return the amount of hours with factor."""
        factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        to_inv = 0.00
        if not to_invoice_id:
            return to_inv
        to_invoice = factor_obj.browse(cr, uid, to_invoice_id)
        # We cannot have negativ hours...
        if to_invoice.factor > 100:
            to_inv = 0.0
        else:
            to_inv = self._compute_hours_factor(hours, to_invoice.factor)
        return to_inv

    def _get_hours_with_factor(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        for rec in self.browse(cr, uid, ids, context):
            tmp_res = self._compute_proj_unit(cr, uid, rec.product_uom_id.id, rec.unit_amount)
            to_inv = self._compute_hours_factor(tmp_res, rec.to_invoice.factor)
            result[rec.id] = {'hours' : tmp_res,
                              'hours_to_inv' : to_inv}
        return result
        
    
    _columns={
        'hours_to_inv': fields.function(_get_hours_with_factor, 
                                        multi='time_cmnpt',
                                        string='Deduced Time', 
                                        method=True, 
                                        type='float', 
                                        store={'account.analytic.line': 
                                               (lambda self, cr, uid, ids, c={}: ids, ['to_invoice','unit_amount','product_uom_id'], 5)}, 
                                        help="This field is the unit amount in hours including"
                                             " the invoice factor (eg. 10h with 60% => 6h)."),
            
        'hours': fields.function(_get_hours_with_factor,
                                 multi='time_cmnpt',
                                 string='Deduced Time',
                                 method=True,
                                 type='float', 
                                 store={'account.analytic.line':
                                        (lambda self, cr, uid, ids, c={}: ids, ['unit_amount','product_uom_id'], 5)}, 
                                 help="This field is the unit amount in hours."),
    }
    
    def _get_hr_analytic_ids(self, cr, uid, ids, context=None):
        """Take an id list of AAL and return a dict with :
            {    
                aal : ids of analytic_line without hr.analytic.timesheet 
                hral : ds of the related hr.analytic.line
            }
        """
        if context is None:
            context = {}
        ts_line_obj = self.pool.get('hr.analytic.timesheet')
        ## if we received an int we convert it into an array
        if isinstance(ids,int):
            ids = [ids]
        ts_ids = ts_line_obj.search(cr, uid, [('line_id','in',ids)])
        hral = []
        aal = []
        for ts_line in ts_line_obj.browse(cr, uid, ts_ids, context):
            # We add all hr.analytic ts
            hral.append(ts_line.id)
            aal.append(ts_line.line_id.id)
        if not context.get('preserve_aa_lines', False):
            # We keep in aal only aal (remove aal from ids and take it)
            # seems to be dead code TOCHECK
            aal = list(set(ids).difference(aal))
        return {'aal':aal,'hral':hral}
                
    def write(self, cr, uid, ids, vals, context=None):
        ts_line = self.pool.get('hr.analytic.timesheet')
        res_dict = self._get_hr_analytic_ids(cr,uid,ids,context)
        # Check if we have related hr.analytic.timesheet, launch
        # the indicator computation of task and hr.analytic lines
        if res_dict['hral']:
            res = ts_line._onwrite_manage_proj_indicators(cr, uid, res_dict['hral'], vals, context)
        res = super(analytic_account_line, self).write(cr, uid, ids, vals, context)
        return res
    
 
    def unlink(self, cr, uid, ids, context=None):
        ts_line = self.pool.get('hr.analytic.timesheet')
        res_dict = self._get_hr_analytic_ids(cr, uid, ids)
        # Check if we have related hr.analytic.timesheet, launch
        # the indicator computation of task and hr.analytic lines
        if res_dict['hral']:
            res = ts_line._onunlink_manage_proj_indicators(cr, uid, res_dict['hral'], context=context)
        res = super(analytic_account_line,self).unlink(cr, uid, ids, context=context)
        return res

analytic_account_line()
