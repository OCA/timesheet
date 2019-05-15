# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = 'project.project'

    timesheet_rounding_granularity = fields.Float(
        string='Timesheet rounding granularity',
        default=0.0,
        help="""1.0 = hour
            0.25 = 15 min
            0.084 ~= 5 min
            0.017 ~= 1 min
            """
    )
    timesheet_rounding_method = fields.Selection(
        string='Timesheet rounding method',
        selection=[
            ('UP', 'Up'),
            ('HALF_UP', 'Closest'),
            ('DOWN', 'Down'),
        ],
        default='UP',
        required=True
    )
    timesheet_invoicing_factor = fields.Float(
        string='Timesheet invoicing factor in percentage',
        default=100.0
    )

    _sql_constraints = [
        (
            'check_timesheet_invoicing_factor',
            'CHECK(0 <= timesheet_invoicing_factor '
            'AND timesheet_invoicing_factor <= 500)',
            'Timesheet invoicing factor should stay between 0 and 500,'
            ' endpoints included.'
        )
    ]
