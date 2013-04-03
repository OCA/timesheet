# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
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

from osv import osv, fields

TASK_WATCHERS = ['work_ids', 'remaining_hours', 'planned_hours']
TIMESHEET_WATCHERS = ['unit_amount', 'product_uom_id', 'account_id', 'to_invoice', 'task_id']

class ProjectTask(osv.Model):
    _inherit = "project.task"
    _name = "project.task"


    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        """TODO improve code taken for OpenERP"""
        res = {}
        cr.execute("""SELECT task_id, COALESCE(SUM(unit_amount),0) 
                        FROM account_analytic_line 
                      WHERE task_id IN %s 
                      GROUP BY task_id""", (tuple(ids),))
                      
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {}
            res[task.id]['effective_hours'] = hours.get(task.id, 0.0)
            res[task.id]['total_hours'] = (task.remaining_hours or 0.0) + hours.get(task.id, 0.0)
            res[task.id]['delay_hours'] = res[task.id]['total_hours'] - task.planned_hours
            res[task.id]['progress'] = 0.0
            if (task.remaining_hours + hours.get(task.id, 0.0)):
                res[task.id]['progress'] = round(min(100.0 * hours.get(task.id, 0.0) / res[task.id]['total_hours'], 99.99), 2)
            if task.state in ('done', 'cancelled'):
                res[task.id]['progress'] = 100.0
        return res


    def _get_analytic_line(self, cr, uid, ids, context=None):
        result = []
        for aal in self.pool.get('account.analytic.line').browse(cr, uid, ids, context=context):
            if aal.task_id: result.append(aal.task_id.id)
        return result


    _columns = {'work_ids': fields.one2many('hr.analytic.timesheet', 'task_id', 'Work done'),
                

    'effective_hours': fields.function(_progress_rate, multi="progress", method=True, string='Time Spent',
                                       help="Sum of spent hours of all tasks related to this project and its child projects.",
                                       store={'project.task': (lambda self, cr, uid, ids, c={}: ids, TASK_WATCHERS, 20),
                                                'account.analytic.line': (_get_analytic_line, TIMESHEET_WATCHERS, 20)}),

    'delay_hours': fields.function(_progress_rate, multi="progress", method=True, string='Deduced Hours',
                                    help="Sum of spent hours with invoice factor of all tasks related to this project and its child projects.",
                                    store={'project.task': (lambda self, cr, uid, ids, c={}: ids, TASK_WATCHERS, 20),
                                             'account.analytic.line': (_get_analytic_line, TIMESHEET_WATCHERS, 20)}),

    'total_hours': fields.function(_progress_rate, multi="progress", method=True, string='Total Time',
                                   help="Sum of total hours of all tasks related to this project and its child projects.",
                                   store={'project.task': (lambda self, cr, uid, ids, c={}: ids, TASK_WATCHERS, 20),
                                            'account.analytic.line': (_get_analytic_line, TIMESHEET_WATCHERS, 20)}),

    'progress': fields.function(_progress_rate, multi="progress", method=True, string='Progress', type='float', group_operator="avg",
                                     help="Percent of tasks closed according to the total of tasks todo.",
                                     store={'project.task': (lambda self, cr, uid, ids, c={}: ids, TASK_WATCHERS, 20),
                                              'account.analytic.line': (_get_analytic_line, TIMESHEET_WATCHERS, 20)})}
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(ProjectTask, self).write(cr, uid, ids, vals, context=context)
        if 'project_id' in vals:
            ts_obj = self.pool.get('hr.analytic.timesheet')
            project_obj = self.pool.get('project.project')
            project = project_obj.browse(cr, uid, vals['project_id'], context)
            account_id = project.analytic_account_id.id
            for task in self.browse(cr, uid, ids, context=context):
                ts_obj.write(cr, uid, [w.id for w in task.work_ids], {'account_id': account_id}, context=context)
        return res

class HrAnalyticTimesheet(osv.Model):
    _inherit = "hr.analytic.timesheet"
    _name = "hr.analytic.timesheet"

    def on_change_unit_amount(self, cr, uid, sheet_id, prod_id, unit_amount, company_id,
                              unit=False, journal_id=False, task_id=False, to_invoice=False, context=None):
        res = super(HrAnalyticTimesheet, self).on_change_unit_amount(cr,
                                                                     uid,
                                                                     sheet_id,
                                                                     prod_id,
                                                                     unit_amount,
                                                                     company_id,
                                                                     unit,
                                                                     journal_id,
                                                                     context)
        if 'value' in res and task_id:
            task_obj = self.pool.get('project.task')
            p = task_obj.browse(cr, uid, task_id).project_id
            if p:
                res['value']['account_id'] = p.analytic_account_id.id
                if p.to_invoice and not to_invoice:
                    res['value']['to_invoice'] = p.to_invoice.id
        return res

class AccountAnalyticLine(osv.Model):
    """We add task_id on AA and manage update of linked task indicators"""
    _inherit = "account.analytic.line"
    _name = "account.analytic.line"



    _columns = {'task_id': fields.many2one('project.task', 'Task')}


    def _compute_hours_with_factor(self, cr, uid, hours, factor_id, context=None):
        if not hours or not factor_id:
            return 0.0
        fact_obj = self.pool.get('hr_timesheet_invoice.factor')
        factor = 100.0 - float(fact_obj.browse(cr, uid, factor_id).factor)
        return (float(hours) / 100.00) * factor

    def _set_remaining_hours_create(self, cr, uid, vals, context=None):
        if not vals.get('task_id'):
            return
        hours = vals.get('unit_amount', 0.0)
        factor_id = vals.get('to_invoice')
        comp_hours = self._compute_hours_with_factor(cr, uid, hours, factor_id, context)
        if comp_hours:
            cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s',
                       (comp_hours, vals['task_id']))
        return vals

    def _set_remaining_hours_write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            # in OpenERP if we set a value to nil vals become False
            old_task_id = line.task_id and line.task_id.id or None
            new_task_id = vals.get('task_id', old_task_id)  # if no task_id in vals we assume it is equal to old

            # we look if value has changed
            if (new_task_id != old_task_id) and old_task_id:
                self._set_remaining_hours_unlink(cr, uid, [line.id], context)
                if new_task_id:
                    data = {'task_id': new_task_id,
                            'to_invoice': vals.get('to_invoice',
                                               line.to_invoice and line.to_invoice.id or False),
                            'unit_amount': vals.get('unit_amount', line.unit_amount)}
                    self._set_remaining_hours_create(cr, uid, data, context)
                return ids
            if new_task_id:
                hours = vals.get('unit_amount', line.unit_amount)
                factor_id = vals.get('to_invoice', line.to_invoice and line.to_invoice.id or False)
                comp_hours = self._compute_hours_with_factor(cr, uid, hours, factor_id, context)
                old_factor = line.to_invoice and line.to_invoice.id or False
                old_comp_hours = self._compute_hours_with_factor(cr, uid, line.unit_amount,
                                                                 old_factor, context)
                # we always execute request because invoice factor can be set to gratis
                cr.execute('update project_task set remaining_hours=remaining_hours - %s + (%s) where id=%s',
                               (comp_hours, old_comp_hours, new_task_id))
        return ids


    def _set_remaining_hours_unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            if not line.task_id:
                continue
            hours = line.unit_amount or 0.0
            factor_id = line.to_invoice and line.to_invoice.id or False
            comp_hours = self._compute_hours_with_factor(cr, uid, hours, factor_id, context)
            if comp_hours:
                cr.execute('update project_task set remaining_hours=remaining_hours + %s where id=%s',
                           (comp_hours, line.task_id.id))
        return ids



    def create(self, cr, uid, vals, context=None):
        if vals.get('task_id'):
            self._set_remaining_hours_create(cr, uid, vals, context)
        return super(AccountAnalyticLine, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        self._set_remaining_hours_write(cr, uid, ids, vals, context=context)
        return super(AccountAnalyticLine, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        self._set_remaining_hours_unlink(cr, uid, ids, context)
        return super(AccountAnalyticLine, self).unlink(cr, uid, ids, context=context)
