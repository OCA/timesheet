# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    timesheet_rounding_unit = fields.Float(
        string="Timesheet rounding unit",
        default=0.0,
        help="""1.0 = hour
            0.25 = 15 min
            0.084 ~= 5 min
            0.017 ~= 1 min
            """,
    )
    timesheet_rounding_method = fields.Selection(
        string="Timesheet rounding method",
        selection=[
            ("NO", "No rounding"),
            ("UP", "Up"),
            ("HALF_UP", "Closest"),
            ("DOWN", "Down"),
        ],
        default="NO",
        required=True,
        help="If you activate the rounding of timesheet lines, only new "
        "entries will be rounded (i.e. existing lines will not be "
        "rounded automatically).",
    )
    timesheet_rounding_factor = fields.Float(
        string="Timesheet rounding factor in percentage", default=100.0
    )

    _sql_constraints = [
        (
            "check_timesheet_rounding_factor",
            "CHECK(0 <= timesheet_rounding_factor "
            "AND timesheet_rounding_factor <= 500)",
            "Timesheet rounding factor should stay between 0 and 500,"
            " endpoints included.",
        )
    ]
