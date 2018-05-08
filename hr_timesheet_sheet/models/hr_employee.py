# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    timesheet_count = fields.Integer(
        compute='_compute_timesheet_count',
        string='Timesheet Sheets',
    )

    @api.multi
    def _compute_timesheet_count(self):
        for employee in self:
            employee.timesheet_count = employee.env['hr_timesheet.sheet'].\
                search_count([('employee_id', '=', employee.id)])
