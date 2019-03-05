# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    _sql_constraints = [
        (
            'project_employee_req',
            (
                'CHECK(('
                '    project_id IS NOT NULL AND employee_id IS NOT NULL'
                ') OR project_id IS NULL)'
            ),
            'Employee is required for Task Log'
        ),
    ]
