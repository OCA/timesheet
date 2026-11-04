# © 2026 Solvos Consultoría Informática (<https://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    timesheet_edit_level = fields.Selection(
        selection=[("none", "None"), ("approver", "Officer"), ("all", "All")],
        default="none",
        help="""
        For this leave type, indicates who can edit generated timesheets
        """,
    )
