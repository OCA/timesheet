# Copyright 2025 Innovara Ltd - Manuel Fombuena
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import TransactionCase


class TestAccountAnalyticLineDefaultGet(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Test Project"})
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee"})
        cls.aal_model = cls.env["account.analytic.line"].with_context(
            is_timesheet=True, default_employee_id=cls.employee.id
        )

    def test_project_id_not_autofilled_from_previous_entries(self):
        for _ in range(3):
            self.aal_model.create(
                {
                    "name": "/",
                    "project_id": self.project.id,
                    "employee_id": self.employee.id,
                    "unit_amount": 1,
                }
            )

        # Sanity check: these are the entries core uses to pick the project
        last_timesheets = self.aal_model.search(
            self.aal_model._get_favorite_project_id_domain(self.employee.id),
            limit=5,
        )
        self.assertEqual(len(last_timesheets), 3)
        self.assertEqual(last_timesheets.project_id, self.project)

        result = self.aal_model.default_get(["project_id"])

        self.assertFalse(result.get("project_id"))

    def test_project_id_preserved_with_default_project_id_in_context(self):
        aal_model = self.aal_model.with_context(default_project_id=self.project.id)

        result = aal_model.default_get(["project_id"])

        self.assertEqual(result["project_id"], self.project.id)

    def test_project_id_preserved_with_ir_default(self):
        other_project = self.env["project.project"].create({"name": "Other Project"})
        for _ in range(3):
            self.aal_model.create(
                {
                    "name": "/",
                    "project_id": other_project.id,
                    "employee_id": self.employee.id,
                    "unit_amount": 1,
                }
            )
        self.env["ir.default"].set(
            "account.analytic.line", "project_id", self.project.id
        )

        result = self.aal_model.default_get(["project_id"])

        self.assertEqual(result["project_id"], self.project.id)

    def test_project_id_kept_when_ir_default_is_the_favourite_project(self):
        for _ in range(3):
            self.aal_model.create(
                {
                    "name": "/",
                    "project_id": self.project.id,
                    "employee_id": self.employee.id,
                    "unit_amount": 1,
                }
            )
        self.env["ir.default"].set(
            "account.analytic.line", "project_id", self.project.id
        )

        result = self.aal_model.default_get(["project_id"])

        self.assertEqual(result["project_id"], self.project.id)
