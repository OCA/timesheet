# Copyright 2025 Innovara Ltd - Manuel Fombuena
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import TransactionCase


class TestAccountAnalyticLineDefaultGet(TransactionCase):
    def test_project_id_removed_when_is_timesheet_without_default_project(self):
        project = self.env["project.project"].create({"name": "Test Project"})
        self.env["ir.default"].set("account.analytic.line", "project_id", project.id)

        context = {
            "is_timesheet": True,
        }

        aal_model = self.env["account.analytic.line"].with_context(**context)
        result = aal_model.default_get(["project_id"])

        self.assertFalse(result.get("project_id"))

    def test_project_id_preserved_with_default_project_id_in_context(self):
        context = {
            "is_timesheet": True,
            "default_project_id": 1,
        }

        aal_model = self.env["account.analytic.line"].with_context(**context)
        result = aal_model.default_get(["project_id"])

        self.assertIn("project_id", result)
