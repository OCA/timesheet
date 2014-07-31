# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier (Camptocamp)
#    Author: Vincent Renaville
#    Copyright 2012 Camptocamp SA
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

from openerp.osv import fields, orm
from tools.translate import _
from datetime import datetime, timedelta


def get_number_days_between_dates(date_from, date_to):
    datetime_from = datetime.strptime(date_from, '%Y-%m-%d')
    datetime_to = datetime.strptime(date_to, '%Y-%m-%d')
    difference = datetime_to - datetime_from
    # return result and add a day
    return difference.days + 1


class HrTimesheetFulfill(orm.TransientModel):
    _name = 'hr.timesheet.fulfill'
    _description = "Wizard to fill-in timesheet for many days"

    _columns = {
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'description': fields.char('Description', size=100, required=True),
        'nb_hours': fields.float('Hours per Day', digits=(2, 2), required=True),
        'analytic_account_id': fields.many2one(
            'account.analytic.account', 'Analytic Account', required=True,
            domain="[('type', '<>', 'view'),"
                   "('state', '!=', 'pending'),"
                   "('state', '!=', 'close')]"),
        'task_id': fields.many2one('project.task', 'Task', required=False)
    }

    def fulfill_timesheet(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool['hr.employee']
        timesheet_obj = self.pool['hr_timesheet_sheet.sheet']
        al_ts_obj = self.pool['hr.analytic.timesheet']
        attendance_obj = self.pool['hr.attendance']
        # get the wizard datas
        wizard = self.browse(cr, uid, ids, context=context)[0]
        # Get the current timesheet
        timesheet_id = context['active_id']
        timesheet = timesheet_obj.browse(
            cr, uid, timesheet_id, context=context)
        # Get the employee
        employee_id = employee_obj.search(
            cr, uid, [('user_id', '=', uid)], context=context)[0]
        employee = employee_obj.browse(cr, uid, employee_id, context=context)
        if not(0.0 <= wizard.nb_hours <= 24.0):
            raise orm.except_orm(
                _('Only 24 hours a day max'),
                _('Please, set another value for nb hours a day.'))
        # compute hours in hours and minutes (tuple)
        hh_mm = divmod(wizard.nb_hours * 60, 60)
        if timesheet.state != 'draft':
            raise orm.except_orm(
                _('UserError'),
                _('You can not modify a confirmed timesheet, please ask the '
                  'manager !'))
        # Verify the date must be in timesheet dates
        if timesheet.date_from > wizard.date_from:
            raise orm.except_orm(
                _('UserError'),
                _('Your date_from must be in timesheet dates !'))
        if timesheet.date_to < wizard.date_to:
            raise orm.except_orm(
                _('UserError'),
                _('Your date_to must be in timesheet dates !'))
        for day in range(get_number_days_between_dates(
                wizard.date_from, wizard.date_to)):
            datetime_current = (datetime.strptime(wizard.date_from, '%Y-%m-%d')
                                + timedelta(days=day)).strftime('%Y-%m-%d')
            unit_id = al_ts_obj._getEmployeeUnit(cr, uid, context)
            product_id = al_ts_obj._getEmployeeProduct(cr, uid, context)
            journal_id = al_ts_obj._getAnalyticJournal(cr, uid, context)
            res = {
                'name': wizard.description,
                'date': datetime_current,
                'unit_amount': wizard.nb_hours,
                'product_uom_id': unit_id,
                'user_id': uid,
                'product_id': product_id,
                'account_id': wizard.analytic_account_id.id,
                'to_invoice': wizard.analytic_account_id.to_invoice.id,
                'task_id': wizard.task_id.id,
                'sheet_id': timesheet.id,
                'journal_id': journal_id,
            }
            on_change_values = al_ts_obj.on_change_unit_amount(
                cr, uid, False, product_id, wizard.nb_hours,
                employee.company_id.id, unit=unit_id, journal_id=journal_id,
                context=context)
            if on_change_values:
                res.update(on_change_values['value'])
            al_ts_obj.create(cr, uid, res, context)
            # If there is no other attendances, create it
            # create the attendances:
            existing_attendances = 0
            att_id = attendance_obj.search(
                cr, uid, [('employee_id', '=', employee_id)])
            for record in attendance_obj.read(cr, uid, att_id, ['name']):
                if record['name'].startswith(datetime_current):
                    existing_attendances = 1
            if not existing_attendances:
                att_date_start = datetime_current + " 00:00:00"
                att_start = {
                    'name': datetime.strptime(att_date_start,
                                              '%Y-%m-%d %H:%M:%S'),
                    'action': 'sign_in',
                    'employee_id': employee_id,
                    'sheet_id': timesheet.id,
                }
                # hh_mm is a tuple (hours, minutes)
                date_end = " %d:%d:00" % (hh_mm[0], hh_mm[1])
                att_end = {
                    'name': datetime.strptime(datetime_current + date_end,
                                              '%Y-%m-%d %H:%M:%S'),
                    'action': 'sign_out',
                    'employee_id': employee_id,
                    'sheet_id': timesheet.id,
                }
                attendance_obj.create(cr, uid, att_start, context)
                attendance_obj.create(cr, uid, att_end, context)
        return {'type': 'ir.actions.act_window_close'}
