# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common


class TestSaleTimesheetBudget(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test account",
                "partner_id": cls.customer.id,
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
        vals = self.project._plan_prepare_values()
        self.assertEqual(vals["dashboard"]["profit"]["budget_amount"], 10)
