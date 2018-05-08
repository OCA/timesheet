# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    timesheet_sheet_to_approve_count = fields.Integer(
        compute='_compute_timesheet_to_approve',
        string='Timesheet Sheets to Approve',
    )

    @api.multi
    def _compute_timesheet_to_approve(self):
        timesheet_data = self.env['hr_timesheet.sheet'].read_group(
            [('department_id', 'in', self.ids), ('state', '=', 'confirm')],
            ['department_id'], ['department_id'])
        result = dict(
            (data['department_id'][0], data['department_id_count'])
            for data in timesheet_data
        )
        for department in self:
            department.timesheet_sheet_to_approve_count = \
                result.get(department.id, 0)
