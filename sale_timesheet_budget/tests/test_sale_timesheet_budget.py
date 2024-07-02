# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleTimesheetBudget(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test plan"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test account",
                "partner_id": cls.customer.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test project",
                "partner_id": cls.customer.id,
                "analytic_account_id": cls.analytic_account.id,
                "allow_billable": True,
            }
        )

    def test_project_budget(self):
        project_form = Form(self.project)
        with project_form.budget_ids.new() as budget_form:
            budget_form.sale_order_id = self.sale_order
            budget_form.quantity = 2
            budget_form.price_unit = 10
        with project_form.budget_ids.new() as budget_form:
            budget_form.sale_order_id = self.sale_order
            budget_form.quantity = -1
            budget_form.price_unit = 10
        project_form.save()
        self.assertEqual(self.project.budget_amount, 10)
        labels = self.project._get_profitability_labels()
        self.assertIn("budgets", labels)
        data = self.project.get_panel_data()
        revenues = data["profitability_items"]["revenues"]
        self.assertEqual(len(revenues["data"]), 1)
        revenues_data = revenues["data"][0]
        self.assertEqual(revenues_data["id"], "budgets")
        self.assertEqual(revenues_data["invoiced"], 0)
        self.assertEqual(revenues_data["to_invoice"], 10)
        expected_action = {"name": "action_profitability_budget_item", "type": "object"}
        self.assertEqual(revenues_data["action"], expected_action)
        self.assertEqual(revenues["total"]["invoiced"], 0)
        self.assertEqual(revenues["total"]["to_invoice"], 10)
        res = self.project.action_profitability_budget_item()
        records = self.env[res["res_model"]].search(res["domain"])
        self.assertEqual(len(records), 2)
        self.assertEqual(sum(records.mapped("amount")), 10)
