# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    timesheet_count = fields.Integer(
        compute='_compute_timesheet_count',
        string='Timesheet Sheets',
    )

    @api.multi
    def _compute_timesheet_count(self):
        Sheet = self.env['hr_timesheet.sheet']
        for employee in self:
            employee.timesheet_count = Sheet.search_count([
                ('employee_id', '=', employee.id)])

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self.sudo():
            if not rec.company_id:
                continue
            for field in [rec.env['hr_timesheet.sheet'].search([
                ('employee_id', '=', rec.id),
                ('company_id', '!=', rec.company_id.id),
                ('company_id', '!=', False),
            ], limit=1)]:
                if rec.company_id and field.company_id and \
                        rec.company_id != field.company_id:
                    raise ValidationError(_(
                        'You cannot change the company, as this %s (%s) '
                        'is assigned to %s (%s).'
                    ) % (rec._name, rec.display_name,
                         field._name, field.display_name))
