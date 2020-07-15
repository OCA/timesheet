# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('user_id')
    def onchange_employee_id_line(self):
        domain = {'employee_id': []}
        hr_emp_obj = self.env['hr.employee']
        employee_id = hr_emp_obj.search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if employee_id and employee_id.allow_timesheet_for:
            if employee_id.allow_timesheet_for == 'anyone':
                domain = {'employee_id': []}
            elif employee_id.allow_timesheet_for == 'self':
                domain = {'employee_id': [
                    ('id', '=', employee_id.id)]}
            elif employee_id.allow_timesheet_for == 'subordinates_only':
                domain = {'employee_id': [
                    ('id', 'in', employee_id.child_ids.ids)]}
            else:
                domain = {'employee_id': [
                    '|', ('id', 'in', employee_id.child_ids.ids),
                    ('id', '=', employee_id.id)]}
        return {'domain': domain}
