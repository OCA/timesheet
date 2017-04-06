# -*- coding: utf-8 -*-
# Copyright 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        store=True,
        compute='_compute_employee_id')

    @api.depends('user_id')
    def _compute_employee_id(self):
        for line in self:
            if line.is_timesheet and line.user_id:
                employees = line.user_id.employee_ids
                if len(employees) == 1:
                    line.employee_id = employees
                elif len(employees) == 0:
                    raise ValidationError(_(
                        'No employee attached to the '
                        'user %s was found.') % line.user_id.name)
                else:
                    raise ValidationError(_(
                        'The user %(user)s is attached to more than one '
                        'employee. These employees are : %(employee)s.') % {
                        'user': line.user_id.name,
                        'employee': [e.name for e in employees],
                    })
