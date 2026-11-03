# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import new_test_user, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProjectTimeTypeCompany(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.time_type_model = cls.env["project.time.type"]
        cls.company_a = cls.env.company
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})
        cls.user_a = new_test_user(
            cls.env,
            login="time_type_user_a",
            groups="base.group_user",
            company_id=cls.company_a.id,
        )
        cls.user_b = new_test_user(
            cls.env,
            login="time_type_user_b",
            groups="base.group_user",
            company_id=cls.company_b.id,
        )
        cls.type_a = cls.time_type_model.create({"name": "Type A"})
        cls.type_b = cls.time_type_model.create(
            {"name": "Type B", "company_id": cls.company_b.id}
        )
        cls.type_shared = cls.time_type_model.create(
            {"name": "Shared Type", "company_id": False}
        )

    def test_company_scope_and_shared_types(self):
        types_a = self.time_type_model.with_user(self.user_a).search([])
        types_b = self.time_type_model.with_user(self.user_b).search([])
        self.assertIn(self.type_a, types_a)
        self.assertNotIn(self.type_b, types_a)
        self.assertIn(self.type_b, types_b)
        self.assertNotIn(self.type_a, types_b)
        self.assertIn(self.type_shared, types_a)
        self.assertIn(self.type_shared, types_b)
