# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    timesheet_emp_ids = fields.Many2many(
        "hr.employee", related="create_uid.timesheet_employee_ids")

    @api.onchange('user_id')
    def onchange_employee_id_line(self):
        domain = {'employee_id': [
            ('id', 'in', self.env.user.timesheet_employee_ids.ids)]}
        return {'domain': domain}
