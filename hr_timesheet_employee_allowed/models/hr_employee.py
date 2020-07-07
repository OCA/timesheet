# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    allow_timesheet_for = fields.Selection(
        [('anyone', 'Anyone'),
         ('self', 'Self'),
         ('subordinates_only', 'Subordinates only'),
         ('self_and_subordinates', 'Self and Subordinates')],
        string="Can enter timesheet for")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=None):
        if self._context.get('from_task_timesheet_line'):
            employee_id = self.search(
                [('user_id', '=', self.env.user.id)], limit=1)
            args_new = None
            if employee_id and employee_id.allow_timesheet_for:
                if employee_id.allow_timesheet_for == 'self':
                    args_new = [('id', '=', employee_id.id)]
                elif employee_id.allow_timesheet_for == 'subordinates_only':
                    args_new = [('id', 'in', employee_id.child_ids.ids)]
                elif employee_id.allow_timesheet_for == \
                        'self_and_subordinates':
                    args_new = ['|', ('id', 'in', employee_id.child_ids.ids),
                                ('id', '=', employee_id.id)]
                else:
                    args_new = []
                args += args_new
        return super(HrEmployee, self).name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit)
