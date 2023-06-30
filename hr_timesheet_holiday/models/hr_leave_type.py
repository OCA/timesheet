# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeaveType(models.Model):
    """Add project to holiday status"""

    _inherit = "hr.leave.type"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        related="timesheet_project_id.analytic_account_id",
    )
