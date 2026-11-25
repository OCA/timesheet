# Copyright 2018 ForgeFlow, S.L.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

_WEEKDAYS = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    sheet_range = fields.Selection(
        [("MONTHLY", "Month"), ("WEEKLY", "Week"), ("DAILY", "Day")],
        string="Timesheet Sheet Range",
        default="WEEKLY",
        help="The range of your Timesheet Sheet.",
    )

    timesheet_week_start = fields.Selection(
        selection=_WEEKDAYS, string="Week start day", default="0"
    )

    timesheet_sheet_review_policy = fields.Selection(
        selection=[
            ("hr", "By HR Officers"),
            ("hr_manager", "By HR Managers"),
            ("timesheet_manager", "By Timesheets Managers"),
        ],
        default="hr",
        help="How Timesheet Sheets review is performed.",
    )
    timesheet_sheet_approver_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Timesheet Approver Field",
        domain=[
            ("model", "=", "hr.employee"),
            ("relation", "=", "res.users"),
            ("ttype", "in", ["many2one", "many2many"]),
        ],
        ondelete="set null",
        help="Employee field pointing to one or more users (res.users). The "
        "users found in this field on the employee can review the employee's "
        "timesheet sheets, in addition to the review policy.",
    )
