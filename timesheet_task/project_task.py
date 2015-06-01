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

from openerp.osv import orm, fields
from openerp import api, SUPERUSER_ID
from openerp.tools.translate import _

TASK_WATCHERS = [
    'work_ids',
    'remaining_hours',
    'effective_hours',
    'planned_hours'
]
TIMESHEET_WATCHERS = [
    'unit_amount',
    'product_uom_id',
    'account_id',
    'task_id'
]


class ProjectTask(orm.Model):
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
            res[task.id]['total_hours'] = (
                task.remaining_hours or 0.0) + hours.get(task.id, 0.0)
            res[task.id]['delay_hours'] = res[task.id][
                'total_hours'] - task.planned_hours
            res[task.id]['progress'] = 0.0
            if (task.remaining_hours + hours.get(task.id, 0.0)):
                res[task.id]['progress'] = round(
                    100.0 * hours.get(task.id, 0.0) /
                    res[task.id]['total_hours'], 2)
        return res

    def _store_set_values(self, cr, uid, ids, fields, context=None):
        # Hack to avoid redefining most of function fields of project.project
        # model. This is mainly due to the fact that orm _store_set_values use
        # direct access to database. So when modify a line the
        # _store_set_values as it uses cursor directly to update tasks
        # project triggers on task are not called

        res = super(ProjectTask, self)._store_set_values(
            cr, uid, ids, fields, context=context)

        if context is None:
            context = {}
        ctx = context.copy()
        if 'recursion' in ctx:
            return res
        ctx['recursion'] = True
        for row in self.browse(cr, SUPERUSER_ID, ids, context=ctx):
            if row.project_id:
                project = row.project_id
                project.write({'parent_id': project.parent_id.id})
        return res

    def _get_analytic_line(self, cr, uid, ids, context=None):
        result = []
        for aal in self.pool['account.analytic.line'].browse(
                cr, uid, ids, context=context):
            if aal.task_id:
                result.append(aal.task_id.id)
        return result

    _columns = {
        'work_ids': fields.one2many(
            'hr.analytic.timesheet', 'task_id', 'Work done'),
        'effective_hours': fields.function(
            _progress_rate, multi="progress", string='Time Spent',
            help="Computed using the sum of the task work done (timesheet "
                 "lines associated on this task).",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)}),
        'delay_hours': fields.function(
            _progress_rate, multi="progress", string='Deduced Hours',
            help="Computed as difference between planned hours by the project "
                 "manager and the total hours of the task.",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)}),
        'total_hours': fields.function(
            _progress_rate, multi="progress", string='Total Time',
            help="Computed as: Time Spent + Remaining Time.",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)}),
        'progress': fields.function(
            _progress_rate, multi="progress", string='Progress', type='float',
            group_operator="avg",
            help="If the task has a progress of 99.99% you should close the "
                 "task if it's finished or reevaluate the time",
            store={'project.task': (lambda self, cr, uid, ids, c=None: ids,
                                    TASK_WATCHERS, 20),
                   'account.analytic.line': (_get_analytic_line,
                                             TIMESHEET_WATCHERS, 20)})
    }

    def write(self, cr, uid, ids, vals, context=None):
        res = super(ProjectTask, self).write(
            cr, uid, ids, vals, context=context)
        if vals.get('project_id'):
            ts_obj = self.pool.get('hr.analytic.timesheet')
            project_obj = self.pool.get('project.project')
            project = project_obj.browse(
                cr, uid, vals['project_id'], context=context)
            account_id = project.analytic_account_id.id
            for task in self.browse(cr, uid, ids, context=context):
                ts_obj.write(cr, uid, [w.id for w in task.work_ids],
                             {'account_id': account_id}, context=context)
        return res


class HrAnalyticTimesheet(orm.Model):

    """
    Add field:
    - hr_analytic_timesheet_id:
    This field is added to make sure a hr.analytic.timesheet can be used
    instead of a project.task.work.

    This field will always return false as we want to by pass next operations
    in project.task write method.

    Without this field, it is impossible to write a project.task in which
    work_ids is empty as a check on it would raise an AttributeError.

    This is because, in project_timesheet module, project.task's write method
    checks if there is an hr_analytic_timesheet_id on each work_ids.

        (project_timesheet.py, line 250, in write)
        if not task_work.hr_analytic_timesheet_id:
            continue

    But as we redefine work_ids to be a relation to hr_analytic_timesheet
    instead of project.task.work, hr_analytic_timesheet doesn't exists
    in hr_analytic_timesheet... so it fails.

    An other option would be to monkey patch the project.task's write method...
    As this method doesn't fit with the change of work_ids relation in model.
    """
    _inherit = "hr.analytic.timesheet"
    _name = "hr.analytic.timesheet"

    def on_change_unit_amount(
            self, cr, uid, sheet_id, prod_id, unit_amount, company_id,
            unit=False, journal_id=False, task_id=False, to_invoice=False,
            project_id=False, context=None):
        res = super(HrAnalyticTimesheet, self).on_change_unit_amount(
            cr, uid, sheet_id, prod_id, unit_amount, company_id, unit,
            journal_id, context=context)
        p = False
        if 'value' in res:
            if task_id:
                task_obj = self.pool['project.task']
                p = task_obj.browse(cr, uid, task_id,
                                    context=context).project_id
            elif project_id:
                p = self.pool['project.project'].browse(
                    cr, uid, project_id, context=context)
            if p:
                res['value']['account_id'] = p.analytic_account_id.id
                if p.to_invoice and not to_invoice:
                    res['value']['to_invoice'] = p.to_invoice.id
        return res

    def _get_dummy_hr_analytic_timesheet_id(
            self, cr, uid, ids, names, arg, context=None):
        """Ensure all hr_analytic_timesheet_id is always False"""
        return dict.fromkeys(ids, False)

    @api.multi
    def on_change_account_id(self, account_id, user_id=False):
        ''' Validate the relation between the project and the task.
            Task must be belong to the project.
        '''
        res = super(HrAnalyticTimesheet, self)\
            .on_change_account_id(account_id=account_id, user_id=user_id)

        if 'value' not in res:
            res['value'] = {}

        task_id = False
        if account_id:
            project_obj = self.env["project.project"]
            projects = project_obj.search([('analytic_account_id',
                                            '=', account_id)])
            if projects:
                assert len(projects) == 1
                project = projects[0]
                if len(project.tasks) == 1:
                    task_id = project.tasks[0].id

        res['value']['task_id'] = task_id
        return res

    _columns = {
        'hr_analytic_timesheet_id': fields.function(
            _get_dummy_hr_analytic_timesheet_id, string='Related Timeline Id',
            type='boolean')
    }


class AccountAnalyticLine(orm.Model):
    """We add task_id on AA and manage update of linked task indicators"""
    _inherit = "account.analytic.line"

    _columns = {
        'task_id': fields.many2one('project.task', 'Task')
    }

    def _check_task_project(self, cr, uid, ids):
        for line in self.browse(cr, uid, ids):
            if line.task_id and line.account_id:
                if line.task_id.project_id.analytic_account_id.id != \
                        line.account_id.id:
                    return False
        return True

    _constraints = [
        (_check_task_project, _('Error! Task must belong to the project.'),
         ['task_id', 'account_id']),
    ]

    def _trigger_projects(self, cr, uid, task_ids, context=None):
        t_obj = self.pool['project.task']
        for task in t_obj.browse(cr, SUPERUSER_ID, task_ids, context=context):
            project = task.project_id
            project.write({'parent_id': project.parent_id.id})
        return task_ids

    def _set_remaining_hours_create(self, cr, uid, vals, context=None):
        if not vals.get('task_id'):
            return
        hours = vals.get('unit_amount', 0.0)
        # We can not do a write else we will have a recursion error
        cr.execute(
            'UPDATE project_task '
            'SET remaining_hours=remaining_hours - %s '
            'WHERE id=%s', (hours, vals['task_id']))
        self._trigger_projects(cr, uid, [vals['task_id']], context=context)
        return vals

    def _set_remaining_hours_write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            # in OpenERP if we set a value to nil vals become False
            old_task_id = line.task_id and line.task_id.id or None
            # if no task_id in vals we assume it is equal to old
            new_task_id = vals.get('task_id', old_task_id)
            # we look if value has changed
            if (new_task_id != old_task_id) and old_task_id:
                self._set_remaining_hours_unlink(cr, uid, [line.id], context)
                if new_task_id:
                    data = {'task_id': new_task_id,
                            'to_invoice': vals.get('to_invoice',
                                                   line.to_invoice.id),
                            'unit_amount': vals.get('unit_amount',
                                                    line.unit_amount)}
                    self._set_remaining_hours_create(cr, uid, data, context)
                    self._trigger_projects(
                        cr, uid, list(set([old_task_id, new_task_id])),
                        context=context)
                return ids
            if new_task_id:
                hours = vals.get('unit_amount', line.unit_amount)
                old_hours = line.unit_amount if old_task_id else 0.0
                # We can not do a write else we will have a recursion error
                cr.execute(
                    'UPDATE project_task '
                    'SET remaining_hours=remaining_hours - %s + (%s) '
                    'WHERE id=%s', (hours, old_hours, new_task_id))
                self._trigger_projects(cr, uid, [new_task_id], context=context)
        return ids

    def _set_remaining_hours_unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for line in self.browse(cr, uid, ids):
            if not line.task_id:
                continue
            hours = line.unit_amount or 0.0
            cr.execute(
                'UPDATE project_task '
                'SET remaining_hours=remaining_hours + %s '
                'WHERE id=%s', (hours, line.task_id.id))
        return ids

    def create(self, cr, uid, vals, context=None):
        if vals.get('task_id'):
            self._set_remaining_hours_create(cr, uid, vals, context)
        return super(AccountAnalyticLine, self).create(cr, uid, vals,
                                                       context=context)

    def write(self, cr, uid, ids, vals, context=None):
        self._set_remaining_hours_write(cr, uid, ids, vals, context=context)
        return super(AccountAnalyticLine, self).write(cr, uid, ids, vals,
                                                      context=context)

    def unlink(self, cr, uid, ids, context=None):
        self._set_remaining_hours_unlink(cr, uid, ids, context)
        return super(AccountAnalyticLine, self).unlink(cr, uid, ids,
                                                       context=context)
