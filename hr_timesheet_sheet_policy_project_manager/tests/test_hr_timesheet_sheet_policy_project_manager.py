# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import users
from odoo.tools import mute_logger

from odoo.addons.hr_timesheet_sheet.tests.test_hr_timesheet_sheet import (
    TestHrTimesheetSheetCommon,
)


class TestHrTimesheetSheetPolicyProjectManager(TestHrTimesheetSheetCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_manager_user_1 = cls.user_3
        cls.project_manager_user_2 = cls.user_4

    @mute_logger("odoo.models.unlink")
    @users("test_user")
    def test_review_policy_capture(self):
        self.company.timesheet_sheet_review_policy = "project_manager"
        sheet_model = self.sheet_model.with_user(self.env.user)
        sheet = sheet_model.create({"project_id": self.project_1.id})
        self.assertEqual(sheet.review_policy, "project_manager")
        self.company.timesheet_sheet_review_policy = "hr"
        self.assertEqual(sheet.review_policy, "project_manager")
        sheet.unlink()
        self.assertFalse(sheet.exists())

    @mute_logger("odoo.models.unlink")
    def test_project_manager_review_policy(self):
        self.company.timesheet_sheet_review_policy = "project_manager"
        timesheet_0 = self.aal_model.with_user(self.user).create(
            {
                "name": "test",
                "project_id": self.project_2.id,
                "employee_id": self.employee.id,
            }
        )
        timesheet_1 = self.aal_model.with_user(self.user).create(
            {
                "name": "test",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
            }
        )
        with self.assertRaises(UserError):
            self.sheet_model.with_user(self.user).create(
                {"company_id": self.employee.company_id.id}
            )
        sheet = self.sheet_model.with_user(self.user).create(
            {
                "company_id": self.employee.company_id.id,
                "project_id": self.project_1.id,
            }
        )
        with self.assertRaises(UserError):
            sheet.project_id = False
        self.company.timesheet_sheet_review_policy = "hr"
        sheet._onchange_project_id()
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)
        with self.assertRaises(UserError):
            sheet.with_user(self.project_manager_user_2).action_timesheet_done()
        with self.assertRaises(UserError):
            sheet.with_user(self.project_manager_user_2).action_timesheet_draft()
        sheet.action_timesheet_confirm()
        self.assertFalse(sheet.with_user(self.user).can_review)
        self.assertEqual(
            self.sheet_model.with_user(self.user).search_count(
                [("can_review", "=", True)]
            ),
            0,
        )
        with self.assertRaises(UserError):
            sheet.with_user(self.user).action_timesheet_done()
        sheet.with_user(self.project_manager_user_1).action_timesheet_done()
        sheet.with_user(self.project_manager_user_1).action_timesheet_draft()
        sheet.unlink()
        self.assertFalse(sheet.exists())
        timesheet_0.unlink()
        self.assertFalse(timesheet_0.exists())
        timesheet_1.unlink()
        self.assertFalse(timesheet_1.exists())

    @mute_logger("odoo.models.unlink")
    @users("test_user")
    def test_project_manager_review_policy_project_required(self):
        sheet_model = self.sheet_model.with_user(self.env.user)
        sheet = sheet_model.new(
            {
                "date_start": self.sheet_model._default_date_start(),
                "date_end": self.sheet_model._default_date_end(),
                "review_policy": "project_manager",
                "state": "new",
            }
        )
        values = sheet._convert_to_write(sheet._cache)
        with self.assertRaises(UserError):
            sheet_model.create(values)
        sheet.project_id = self.project_1
        values.update(sheet._convert_to_write(sheet._cache))
        sheet = sheet_model.create(values)
        with self.assertRaises(UserError):
            sheet.project_id = False
        sheet.unlink()
        self.assertFalse(sheet.exists())

    @mute_logger("odoo.models.unlink")
    @users("test_user")
    def test_project_manager_review_policy_overlapping(self):
        self.company.timesheet_sheet_review_policy = "project_manager"
        sheet_model = self.sheet_model.with_user(self.env.user)
        sheet1 = sheet_model.create({"project_id": self.project_1.id})
        with self.assertRaises(ValidationError):
            sheet2 = sheet_model.create({"project_id": self.project_1.id})
        sheet2 = sheet_model.create({"project_id": self.project_2.id})
        with self.assertRaises(ValidationError):
            sheet2.write({"project_id": self.project_1.id})
        self.company.timesheet_sheet_review_policy = "hr"
        sheet1.unlink()
        self.assertFalse(sheet1.exists())
        sheet2.unlink()
        self.assertFalse(sheet2.exists())
