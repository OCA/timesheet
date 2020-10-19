# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    timesheet_employee_ids = fields.Many2many(
        "hr.employee",
        compute="calc_timesheet_employees_for_user",
        string='Timesheet Employees',
    )

    @api.multi
    def calc_timesheet_employees_for_user(self):
        emp_obj = self.env['hr.employee']
        for user_id in self:
            user_id.timesheet_employee_ids = []

            employee = emp_obj.search(
                [('user_id', '=', user_id.id)], limit=1)

            if employee and employee.allow_timesheet_for:

                if employee.allow_timesheet_for == 'anyone':
                    employees = emp_obj.search([]).ids
                    user_id.timesheet_employee_ids = [(6, 0, employees)]

                elif employee.allow_timesheet_for == 'self':
                    user_id.timesheet_employee_ids = [(6, 0, [employee.id])]

                elif employee.allow_timesheet_for == 'subordinates_only':
                    employees = emp_obj.search(
                        [('id', 'in', employee.child_ids.ids)]).ids
                    user_id.timesheet_employee_ids = [(6, 0, employees)]

                else:
                    employees = emp_obj.search(
                        ['|', ('id', 'in', employee.child_ids.ids),
                         ('id', '=', employee.id)]).ids
                    user_id.timesheet_employee_ids = [(6, 0, employees)]
            else:
                user_id.write({'timesheet_employee_ids': [(6, 0, [])]})
