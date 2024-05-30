# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, new_test_user


class TestHrTimesheetSheetPolicyDepartmentManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.HrTimesheetSheet = cls.env["hr_timesheet.sheet"]
        cls.company = cls.env["res.company"].create(
            {
                "name": "Company",
            }
        )
        cls.env.user.company_ids += cls.company
        cls.department_manager_user = new_test_user(
            cls.env,
            "department_manager_user",
            groups="hr_timesheet.group_hr_timesheet_user,"
            "project.group_project_user,base.group_multi_company",
            company_id=cls.company.id,
            context={
                "no_reset_password": True,
                "company_ids": cls.company.ids,
            },
        )
        cls.employee_user = new_test_user(
            cls.env,
            "employee_user",
            groups="hr.group_hr_user,hr_timesheet.group_hr_timesheet_user,"
            "project.group_project_user,base.group_multi_company",
            company_id=cls.company.id,
            context={
                "no_reset_password": True,
                "company_ids": cls.company.ids,
            },
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Employee",
                "user_id": cls.employee_user.id,
                "company_id": cls.company.id,
            }
        )
        cls.department_manager = cls.env["hr.employee"].create(
            {
                "name": "Department Manager",
                "user_id": cls.department_manager_user.id,
                "company_id": cls.company.id,
            }
        )
        cls.department = cls.env["hr.department"].create(
            {
                "name": "Department",
                "company_id": cls.company.id,
                "manager_id": cls.department_manager.id,
            }
        )

    def test_review_policy_capture(self):
        self.company.timesheet_sheet_review_policy = "department_manager"
        sheet = self.HrTimesheetSheet.with_user(self.employee_user).create(
            {
                "company_id": self.company.id,
                "department_id": self.department.id,
            }
        )
        self.assertEqual(sheet.review_policy, "department_manager")
        self.company.timesheet_sheet_review_policy = "hr"
        self.assertEqual(sheet.review_policy, "department_manager")
        sheet.unlink()

    def test_department_manager_review_policy(self):
        self.company.timesheet_sheet_review_policy = "department_manager"

        self.HrTimesheetSheet.with_user(self.employee_user).get_view(
            view_type="form",
        )
        self.HrTimesheetSheet.with_user(self.employee_user).get_view(
            view_type="tree",
        )

        sheet = self.HrTimesheetSheet.with_user(self.employee_user).create(
            {
                "company_id": self.company.id,
                "department_id": self.department.id,
            }
        )
        self.company.timesheet_sheet_review_policy = "hr"

        sheet._compute_complete_name()

        sheet.action_timesheet_confirm()
        self.assertFalse(sheet.with_user(self.employee_user).can_review)
        self.assertEqual(
            self.HrTimesheetSheet.with_user(self.employee_user).search_count(
                [("can_review", "=", True)]
            ),
            0,
        )
        with self.assertRaises(UserError):
            sheet.with_user(self.employee_user).action_timesheet_done()
        sheet.with_user(self.department_manager_user).action_timesheet_done()
        sheet.with_user(self.department_manager_user).action_timesheet_draft()
        sheet.unlink()
