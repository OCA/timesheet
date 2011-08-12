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
from mx import DateTime
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
    unlink can't be done if TS confirmed."""

    _inherit = "account.analytic.line"
    
    def _get_hr_analytic_ids(self,cr,uid,ids,context=None):
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
        ts_ids = ts_line_obj.search(cr,uid,[('line_id','in',ids)])
        hral = []
        aal = []
        for ts_line in ts_line_obj.browse(cr,uid,ts_ids,context):
            # We add all hr.analytic ts
            hral.append(ts_line.id)
            aal.append(ts_line.line_id.id)
        # We keep in aal only aal (remove aal from ids and take it)
        aal = list(set(ids).difference(aal))
        return {'aal':aal,'hral':hral}
                
    def write(self, cr, uid, ids, vals, context=None):
        ts_line = self.pool.get('hr.analytic.timesheet')
        res_dict = self._get_hr_analytic_ids(cr,uid,ids,context)
        # Check if we have related hr.analytic.timesheet, launch
        # the unlink method of hr.analytic.timesheet instead
        if res_dict['hral']:
            res = ts_line._onwrite_manage_proj_indicators(cr,uid,res_dict['hral'],vals,context)
        res = super(analytic_account_line,self).write(cr, uid, ids,vals,context)
        return res
    
 
    def unlink(self, cr, uid, ids, *args, **kwargs):
        ts_line = self.pool.get('hr.analytic.timesheet')
        res_dict = self._get_hr_analytic_ids(cr,uid,ids)
        # Check if we have related hr.analytic.timesheet, launch
        # the unlink method of hr.analytic.timesheet instead
        if res_dict['hral']:
            res = ts_line._onunlink_manage_proj_indicators(cr,uid,res_dict['hral'],*args,**kwargs)
        res = super(analytic_account_line,self).unlink(cr, uid, res_dict['aal'],*args, **kwargs)
        return res

analytic_account_line()

