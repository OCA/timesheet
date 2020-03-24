# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    employee_timesheet_cost_policy = fields.Selection(
        string='Employee\'s Timesheet Cost policy',
        selection=[
            ('contract_avg', 'Contract-wide average'),
            ('annual_avg', 'Annual average'),
            ('monthly_avg', 'Monthly average'),
        ],
        default='monthly_avg',
        help='How Employee\'s Timesheet Cost is calculated',
    )

    use_manual_employee_timesheet_cost = fields.Boolean(
        string='Use manual Employee\'s Timesheet Cost',
        default=True,
    )
