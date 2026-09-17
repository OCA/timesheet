# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetSheetTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reviewer = new_test_user(
            cls.env,
            login="timesheet_tier_reviewer",
            groups="hr.group_hr_user",
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Timesheet Tier Employee",
                "company_id": cls.env.company.id,
                "user_id": cls.reviewer.id,
            }
        )
        cls.env["tier.definition"].create(
            {
                "model_id": cls.env["ir.model"]._get_id("hr_timesheet.sheet"),
                "review_type": "individual",
                "reviewer_id": cls.reviewer.id,
                "definition_domain": "[]",
            }
        )
        start = date(2026, 1, 1)
        cls.sheets = cls.env["hr_timesheet.sheet"].create(
            [
                {
                    "employee_id": cls.employee.id,
                    "date_start": start + timedelta(days=7 * index),
                    "date_end": start + timedelta(days=7 * index + 6),
                    "state": "draft",
                }
                for index in range(3)
            ]
        )

    def test_search_can_review_only_returns_requested_sheet(self):
        requested_sheet = self.sheets[0]
        requested_sheet.action_timesheet_confirm()
        reviews = requested_sheet.request_validation()
        self.assertTrue(reviews)

        sheets_to_review = (
            self.env["hr_timesheet.sheet"]
            .with_user(self.reviewer)
            .search([("can_review", "=", True)])
        )

        self.assertEqual(sheets_to_review, requested_sheet)
