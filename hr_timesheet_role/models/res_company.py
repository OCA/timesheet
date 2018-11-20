# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_timesheet_role_required = fields.Boolean(
        string='Timesheet Role Required',
        default=True,
    )
    limit_timesheet_role_to_assignments = fields.Boolean(
        string='Limit Timesheet Role to Assignments',
        default=False,
    )
