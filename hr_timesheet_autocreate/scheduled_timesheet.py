# -*- coding: utf-8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
##############################################################################

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class scheduled_timesheet(osv.osv):
    _inherit='hr_timesheet_sheet.sheet'
    _track = {
        'state': {
            'hr_timesheet_autocreate.mt_issue_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'hr_timesheet_autocreate.mt_issue_confirm': lambda self, cr, uid, obj, ctx=None:  obj['state'] == 'confirm',
            'hr_timesheet_autocreate.mt_issue_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
        },
    }
    _columns={
          'employee_id': fields.many2one('hr.employee', 'Employee', required=True,track_visibility='always'),
          'state' : fields.selection([
            ('new', 'New'),
            ('draft','Open'),
            ('confirm','Waiting Approval'),
            ('done','Approved')], 'Status', select=True, required=True, readonly=True,track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed timesheet. \
                \n* The \'Confirmed\' status is used for to confirm the timesheet by user. \
                \n* The \'Done\' status is used when users timesheet is accepted by his/her senior.'),
                }
    def update_timesheets(self, cr, uid, context=None):
        #ID for the active employee
        employees=self.pool.get('hr.employee').search(cr,uid,[('active','=',True)])
        date=time.strftime('%Y-%m-%d')
        #for each employee, we check if he has an active contract (compatibility with BHC_hr_timesheet_overtime)
        for idemployes in employees:
            contract=[]
            working_hours=None
            exist=False
            idcontrat=self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',idemployes)])
            for y in idcontrat:
                datedefin=self.pool.get('hr.contract').browse(cr,uid,y).date_end
                datededebut=self.pool.get('hr.contract').browse(cr,uid,y).date_start
                wh=self.pool.get('hr.contract').browse(cr,uid,y).working_hours
                if date <= datedefin and date >= datededebut:
                    contract=y
                    working_hours=wh
                elif not datedefin:
                    contract=y
                    working_hours=wh
            if not contract:
                continue
            #ID of all timesheet by employee 
            sheets=self.pool.get('hr_timesheet_sheet.sheet').search(cr,uid,[('employee_id','=', idemployes)])
            for sheet in sheets:
                timesheet=self.pool.get('hr_timesheet_sheet.sheet').browse(cr,uid,sheet)
                #Check if a timesheet for the actual period already exist 
                if timesheet.date_to >= date:
                    exist=True
                    break
            tab=[]
            if not exist:
                #If no timesheet, we create this one
                id_u=self.pool.get('hr.employee').browse(cr,uid,idemployes).user_id.partner_id.id
                id_user=self.pool.get('hr.employee').browse(cr,uid,idemployes).user_id.id
                id_journal=self.pool.get('hr.employee').browse(cr,uid,idemployes).journal_id.id
                id_gen = self.pool.get('hr.employee').browse(cr,uid,idemployes).product_id.property_account_expense.id
                if not id_gen:
                    id_gen = self.pool.get('hr.employee').browse(cr,uid,idemployes).product_id.categ_id.property_account_expense_categ.id
                tab.append(id_u)
                id_b=self.pool.get('res.users').search(cr,uid,[('name','=','Bertrand Hanot')])
                if id_b:
                    id_b=self.pool.get('res.users').browse(cr,uid,id_b[0]).partner_id.id
                    tab.append(id_b)
                timesheet_tmp=self.pool.get('hr_timesheet_sheet.sheet').create(cr,uid,{'employee_id' : idemployes,'message_follower_ids':[(6,0,tab)]})
                # check if timesheet
                if timesheet_tmp:
                    timesheet=self.pool.get('hr_timesheet_sheet.sheet').browse(cr,uid,timesheet_tmp)
                    date_from=datetime.strptime(timesheet.date_from,"%Y-%m-%d")
                    date_to=datetime.strptime(timesheet.date_to,"%Y-%m-%d")
                    # check for each day in the timesheet
                    while date_from <= date_to:
                        date_from1=date_from.replace(hour=0,minute=1)
                        date_from2=date_from.replace(hour=23,minute=59)
                        date_from11=date_from.strftime("%Y-%m-%d")
                        day=int(date_from.strftime("%u"))-1
                        tmp=self.pool.get("resource.calendar.attendance").search(cr,uid,[('calendar_id','=',working_hours.id),('dayofweek','=',str(day))])
                        if tmp:
                            # check if the day is in days off    
                            obj1=self.pool.get("training.holiday.period")
                            obj1_s=obj1.search(cr,uid,[('active','=',True),('date_start','=',date_from11)])
                            if obj1_s:
                                obj1_b=obj1.browse(cr,uid,obj1_s)
                                if obj1_b[0].categ and obj1_b[0].categ.timesheet:
                                    t=self.pool.get('hr.analytic.timesheet').create(cr, uid,{'sheet_id':timesheet_tmp, 'date': date_from, 'account_id':obj1_b[0].categ.analytic_account_id.id, 'unit_amount':7.5,'name':obj1_b[0].name or '', 'journal_id':id_journal,'user_id':id_user,'general_account_id':id_gen})
                            # check if the day is an holiday
                            obj2=self.pool.get("hr.holidays")
                            date_from1=date_from1.strftime("%Y-%m-%d %H:%M:%S")
                            date_from2=date_from2.strftime("%Y-%m-%d %H:%M:%S")
                            obj2_s=obj2.search(cr,uid,[('employee_id','=',idemployes),('state','=','validate'),('type','=','remove'),('date_from','>',date_from1),('date_from','<',date_from2)])
                            obj2_s2=obj2.search(cr,uid,[('employee_id','=',idemployes),('state','=','validate'),('type','=','remove'),('date_from','<',date_from1),('date_to','>',date_from1)])
                            obj2_s=obj2_s+obj2_s2
                            if obj2_s:
                                timesheet_h=obj2.browse(cr,uid,obj2_s[0]).holiday_status_id.timesheet
                                if timesheet_h:
                                    df=obj2.browse(cr,uid,obj2_s[0]).date_from
                                    dt=obj2.browse(cr,uid,obj2_s[0]).date_to
                                    account_h=obj2.browse(cr,uid,obj2_s[0]).holiday_status_id.analytic_account_id.id
                                    pivot2=datetime.strptime(df,"%Y-%m-%d %H:%M:%S")
                                    pivot=pivot2.replace(hour=11,minute=0)
                                    pivot=pivot.strftime("%Y-%m-%d %H:%M:%S")
                                    tmp3=date_from-pivot2
                                    name=obj2.browse(cr,uid,obj2_s[0]).name or ''
                                    if (df>pivot or dt<pivot) and tmp3.days<0:
                                        h_tmp=3.75
                                    else:
                                        h_tmp=7.5
                                    t=self.pool.get('hr.analytic.timesheet').create(cr, uid,{'sheet_id':timesheet_tmp, 'date': date_from, 'account_id':account_h, 'unit_amount':h_tmp, 'journal_id':id_journal,'name':name or '','user_id':id_user,'general_account_id':id_gen})
                        date_from=date_from + timedelta(days=1)
        return True
    
scheduled_timesheet()

