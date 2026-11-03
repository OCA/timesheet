# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

COST_TYPE_SELECTION = [
    ("employee", "Employee Cost"),
    ("ratio", "Ratio of Employee Cost"),
    ("fixed", "Fixed Hourly Cost"),
]


class ProjectTimeType(models.Model):
    _inherit = "project.time.type"

    cost_type = fields.Selection(
        selection=COST_TYPE_SELECTION,
        default="employee",
        required=True,
        help="How the time type sets the hourly cost of a timesheet line.",
    )
    cost_ratio = fields.Float(
        default=1.0,
        help="Factor applied to the employee hourly cost. 1.0 means 100 %.",
    )
    fixed_cost = fields.Monetary(
        currency_field="currency_id",
        groups="project.group_project_manager,hr.group_hr_user",
        help="Hourly cost used instead of the employee cost, in the company "
        "currency. The rate is positive; the analytic amount carries the sign.",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True,
    )

    @api.constrains("cost_type", "cost_ratio", "fixed_cost")
    def _check_cost_values(self):
        for time_type in self:
            if time_type.cost_type == "fixed" and not time_type.company_id:
                raise ValidationError(
                    self.env._(
                        "The fixed cost of the time type %(time_type)s requires "
                        "a company. A shared time type can use the employee cost "
                        "or a ratio.",
                        time_type=time_type.display_name,
                    )
                )
            if time_type.cost_type == "ratio" and time_type.cost_ratio <= 0:
                raise ValidationError(
                    self.env._(
                        "The cost ratio of the time type %(time_type)s must be "
                        "greater than zero.",
                        time_type=time_type.display_name,
                    )
                )
            if time_type.cost_type == "fixed" and time_type.fixed_cost <= 0:
                raise ValidationError(
                    self.env._(
                        "The fixed cost of the time type %(time_type)s must be "
                        "greater than zero, because it is an hourly rate.",
                        time_type=time_type.display_name,
                    )
                )
