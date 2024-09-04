# Copyright 2024 Tecnativa - Juan José Seguí
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common


class TestAccountAnalyticLine(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticLine, cls).setUpClass()
        cls.AccountAnalyticAccount = cls.env["account.analytic.account"]
        cls.PredefinedDescription = cls.env["timesheet.predefined.description"]
        cls.AccountAnalyticLine = cls.env["account.analytic.line"]
        cls.description = "Test Predefined Description"
        cls.predefined_description = cls.PredefinedDescription.create(
            {"name": cls.description}
        )
        cls.analytic_account = cls.AccountAnalyticAccount.create(
            {"name": "Test Account"}
        )
        cls.analytic_line = cls.AccountAnalyticLine.create(
            {
                "name": "Original Description",
                "account_id": cls.analytic_account.id,
            }
        )

    def test_onchange_predefined_description(self):
        with Form(self.analytic_line) as form:
            form.predefined_description_id = self.predefined_description
            self.assertEqual(form.name, self.description)

    def test_create_predefined_description(self):
        line = self.analytic_line.create(
            {
                "account_id": self.analytic_account.id,
                "predefined_description_id": self.predefined_description.id,
            },
        )
        self.assertEqual(line.name, self.description)

    def test_write_predefined_description(self):
        self.analytic_line.write(
            {"predefined_description_id": self.predefined_description.id}
        )
        self.assertEqual(self.analytic_line.name, self.description)
