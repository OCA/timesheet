# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services, S.L. -
# Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.osv import fields, orm
from openerp.tools.translate import _


class HrPeriodCreateTimesheet(orm.TransientModel):

    _name = 'hr.period.create.timesheet'
    _description = 'Hr Period Create Timesheet'

    _columns = {
        'employee_ids': fields.many2many(
                'hr.employee', 'hr_employee_hr_period_create_timesheet_rel',
                'wiz_id', 'employee_id', 'Employees'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(HrPeriodCreateTimesheet, self).default_get(
            cr, uid, fields, context=context)
        period_obj = self.pool['hr.period']
        employee_obj = self.pool['hr.employee']
        period_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not period_ids:
            return res
        assert active_model == 'hr.period', \
            'Bad context propagation'

        company_id = False
        for period in period_obj.browse(cr, uid, period_ids, context=context):
            if company_id and company_id != period.company_id.id:
                raise orm.except_orm(
                    _('Error !'),
                    _('All periods must belong to the same company.'))
            company_id = period.company_id.id
        employee_ids = employee_obj.search(cr, uid, [
            ('company_id', '=', company_id),
        ], context=context)

        res['employee_ids'] = [(6, 0, employee_ids)]

        return res

    def _prepare_timesheet(self, cr, uid, wiz_data, employee, hr_period,
                           context=None):
        return {
            'employee_id': employee.id,
            'date_from': hr_period.date_start,
            'date_to': hr_period.date_stop,
            'company_id': hr_period.company_id.id,
            'department_id': employee.department_id.id,
            'hr_period_id': hr_period.id
        }

    def compute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        hr_period_obj = self.pool['hr.period']
        timesheet_obj = self.pool['hr_timesheet_sheet.sheet']
        wiz_data = self.browse(cr, uid, ids[0], context=context)
        hr_period_ids = context.get('active_ids', [])
        for employee in wiz_data.employee_ids:
            for hr_period in hr_period_obj.browse(cr, uid, hr_period_ids,
                                                  context=context):
                timesheet_ids = timesheet_obj.search(
                        cr, uid, [('employee_id', '=', employee.id),
                                  ('date_from', '<=', hr_period.date_stop),
                                  ('date_to', '>=', hr_period.date_start)],
                        context=context)
                if timesheet_ids:
                    raise orm.except_orm(
                        _('Error !'),
                        _('Employee %s already has a Timesheet within the '
                          'date range of HR Period %s.') % (employee.name,
                                                            hr_period.name))

                ts_data = self._prepare_timesheet(cr, uid, wiz_data,
                                                  employee, hr_period,
                                                  context=context)
                ts_id = timesheet_obj.create(cr, uid, ts_data, context=context)
                res.append(ts_id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('Employee Timesheets'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr_timesheet_sheet.sheet',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
