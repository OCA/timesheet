# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    budget_ids = fields.One2many(
        comodel_name="project.project.budget",
        inverse_name="project_id",
        string="Budgets",
        copy=False,
    )
    budget_amount = fields.Float(
        compute="_compute_budget_amount", string="Budget Amount"
    )

    @api.depends("budget_ids")
    def _compute_budget_amount(self):
        for item in self:
            item.budget_amount = sum(item.mapped("budget_ids.amount"))

    def _plan_prepare_values(self):
        """Inject the budget amounts in the project overview."""
        res = super()._plan_prepare_values()
        budget_amount = sum(self.mapped("budget_amount"))
        res["dashboard"]["profit"]["budget_amount"] = budget_amount
        res["dashboard"]["profit"]["total"] += budget_amount
        return res


class ProjectProjectBudget(models.Model):
    _name = "project.project.budget"
    _description = "Project Project Budget"
    _order = "date, id"

    date = fields.Date()
    name = fields.Char(string="Concept")
    project_id = fields.Many2one(
        comodel_name="project.project", string="Project", required=True
    )
    allowed_sale_order_ids = fields.Many2many(
        comodel_name="sale.order", compute="_compute_allowed_sale_order_ids"
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        domain="[('id', 'in', allowed_sale_order_ids)]",
    )
    analytic_account_id = fields.Many2one(related="project_id.analytic_account_id")
    quantity = fields.Float(
        string="Quantity", digits="Account", default=1, required=True
    )
    price_unit = fields.Float(string="Product Price", digits="Account", required=True)
    amount = fields.Float(compute="_compute_amount", string="Amount", store=True)

    @api.depends("project_id")
    def _compute_allowed_sale_order_ids(self):
        sale_order_model = self.env["sale.order"].sudo()
        for item in self:
            item.allowed_sale_order_ids = sale_order_model.search(
                [
                    ("partner_id", "=", item.project_id.partner_id.id),
                    (
                        "analytic_account_id",
                        "=",
                        item.project_id.analytic_account_id.id,
                    ),
                ]
            )

    @api.depends("quantity", "price_unit")
    def _compute_amount(self):
        for item in self:
            item.amount = item.quantity * item.price_unit
