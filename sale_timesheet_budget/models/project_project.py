# Copyright 2022-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _lt, api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    budget_ids = fields.One2many(
        comodel_name="project.project.budget",
        inverse_name="project_id",
        string="Budgets",
        copy=False,
    )
    budget_amount = fields.Float(compute="_compute_budget_amount")

    @api.depends("budget_ids")
    def _compute_budget_amount(self):
        data = self.env["project.project.budget"].read_group(
            domain=[("project_id", "in", self.ids)],
            fields=["project_id", "amount:sum"],
            groupby=["project_id"],
        )
        mapped_data = {x["project_id"][0]: x["amount"] for x in data}
        for item in self:
            item.budget_amount = mapped_data.get(item.id, 0)

    def action_profitability_budget_item(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_timesheet_budget.action_project_project_budget"
        )
        action["domain"] = [("project_id", "=", self.id)]
        return action

    def _get_profitability_labels(self):
        res = super()._get_profitability_labels()
        res["budgets"] = _lt("Budgets")
        return res

    def _get_profitability_items(self, with_action=True):
        items = super()._get_profitability_items(with_action)
        if not self.budget_ids:
            return items
        last_sequence = len(items["revenues"]["data"])
        items["revenues"]["data"].append(
            {
                "id": "budgets",
                "sequence": last_sequence + 1,
                "invoiced": 0,
                "to_invoice": self.budget_amount,
                "action": {
                    "name": "action_profitability_budget_item",
                    "type": "object",
                },
            }
        )
        items["revenues"]["total"]["to_invoice"] += self.budget_amount
        return items


class ProjectProjectBudget(models.Model):
    _name = "project.project.budget"
    _description = "Project Project Budget"
    _order = "date, id"

    date = fields.Date()
    name = fields.Char(string="Concept")
    project_id = fields.Many2one(
        comodel_name="project.project", string="Project", required=True
    )
    sale_order_id_domain = fields.Binary(compute="_compute_sale_order_id_domain")
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
    )
    analytic_account_id = fields.Many2one(related="project_id.analytic_account_id")
    quantity = fields.Float(digits="Account", default=1, required=True)
    price_unit = fields.Float(string="Product Price", digits="Account", required=True)
    amount = fields.Float(compute="_compute_amount", store=True)

    @api.depends(
        "project_id", "project_id.partner_id", "project_id.analytic_account_id"
    )
    def _compute_sale_order_id_domain(self):
        for item in self:
            item.sale_order_id_domain = [
                ("partner_id", "=", item.project_id.partner_id.id),
                (
                    "analytic_account_id",
                    "=",
                    item.project_id.analytic_account_id.id,
                ),
                ("state", "!=", "cancel"),
            ]

    @api.depends("quantity", "price_unit")
    def _compute_amount(self):
        for item in self:
            item.amount = item.quantity * item.price_unit
