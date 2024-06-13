# Copyright (C) 2024 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTimeType(models.Model):
    _inherit = "project.time.type"

    apply_cost_rules = fields.Boolean()
    cost_rule_ids = fields.One2many(
        "project.time.type.cost.rule",
        "time_type_id",
    )

    def _apply_cost_rules(self, timesheet, amount):
        """Apply cost rules to the amount based on the employee and the time type."""
        if not self.apply_cost_rules:
            return amount
        for rule in self.cost_rule_ids:
            amount = rule.apply_rule(timesheet, amount)
        return amount


class ProjectTimeTypeCostRule(models.Model):
    _name = "project.time.type.cost.rule"
    _description = "Project Time Type Cost Rule"
    _order = "sequence, id"

    def apply_rule(self, timesheet, amount):
        if self.domain:
            if not self.apply_domain(timesheet):
                return amount

        method_name = f"apply_rule_{self.cost_rule_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(timesheet, amount)
        else:
            raise ValueError(
                f"There is no method to apply the rule type: {self.cost_rule_type}"
            )

    def apply_domain(self, timesheet):
        domain = ast.literal_eval(self.domain)
        return timesheet.employee_id.filtered_domain(domain)

    def apply_rule_fixed(self, timesheet, amount):
        return timesheet.unit_amount * self.fixed_cost

    def apply_rule_ratio(self, timesheet, amount):
        return amount * self.ratio_value

    @api.constrains("fixed_cost", "ratio_value")
    def _check_fixed_cost_ratio_value(self):
        for record in self:
            if record.cost_rule_type == "fixed" and record.fixed_cost > 0:
                raise ValidationError(_("Fixed cost must be negative"))
            if record.cost_rule_type == "ratio" and record.ratio_value < 0:
                raise ValidationError(_("Ratio value must be positive"))

    def _compute_display_value(self):
        for record in self:
            if record.cost_rule_type == "fixed":
                record.display_value = record.fixed_cost
            else:
                record.display_value = record.ratio_value

    sequence = fields.Integer(
        required=True,
    )
    time_type_id = fields.Many2one(
        "project.time.type",
        ondelete="cascade",
        required=True,
    )
    cost_rule_type = fields.Selection(
        [("fixed", "Fixed"), ("ratio", "Ratio")],
        required=True,
    )
    fixed_cost = fields.Float(
        help="Fixed cost for this rule, this will replace"
        " the employee cost or previus rule value"
    )
    ratio_value = fields.Float(
        help="Ratio value for this rule, this will be multiplied"
        " by the employee cost or previus rule value"
    )
    display_value = fields.Float(
        string="Value",
        compute="_compute_display_value",
        help="Value to display in the timesheet line",
    )
    domain = fields.Text(
        help="Domain to apply this rule base on the employee, leave"
        " empty to apply to all employees"
    )
