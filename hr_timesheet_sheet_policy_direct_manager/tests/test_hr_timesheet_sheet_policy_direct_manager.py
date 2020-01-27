# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import common


class TestHrTimesheetSheetPolicyDirectManager(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.HrTimesheetSheet = self.env['hr_timesheet.sheet']
        self.HrEmployee = self.env['hr.employee']
        self.HrDepartment = self.env['hr.department']
        self.ResUsers = self.env['res.users']
        self.ResCompany = self.env['res.company']
        self.group_hr_user = self.env.ref('hr.group_hr_user')
        self.multi_company_group = self.env.ref('base.group_multi_company')
        self.sheet_user_group = self.env.ref(
            'hr_timesheet.group_hr_timesheet_user'
        )
        self.project_user_group = self.env.ref('project.group_project_user')
        self.company = self.ResCompany.create({
            'name': 'Company',
        })
        self.env.user.company_ids += self.company
        self.employee_user = self.ResUsers.with_context({
            'no_reset_password': True,
        }).create({
            'name': 'Employee User',
            'login': 'employee_user',
            'email': 'employee_user@example.com',
            'groups_id': [(6, 0, [
                self.group_hr_user.id,
                self.sheet_user_group.id,
                self.project_user_group.id,
                self.multi_company_group.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })
        self.direct_manager_user = self.ResUsers.with_context({
            'no_reset_password': True,
        }).create({
            'name': 'Direct Manager User',
            'login': 'direct_manager_user',
            'email': 'direct_manager_user@example.com',
            'groups_id': [(6, 0, [
                self.sheet_user_group.id,
                self.project_user_group.id,
                self.multi_company_group.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })
        self.direct_manager = self.HrEmployee.create({
            'name': 'Direct Manager',
            'user_id': self.direct_manager_user.id,
            'company_id': self.company.id,
        })
        self.employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.employee_user.id,
            'parent_id': self.direct_manager.id,
            'company_id': self.company.id,
        })

    def test_review_policy_capture(self):
        self.company.timesheet_sheet_review_policy = 'direct_manager'
        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
        })
        self.assertEqual(sheet.review_policy, 'direct_manager')
        self.company.timesheet_sheet_review_policy = 'hr'
        self.assertEqual(sheet.review_policy, 'direct_manager')
        sheet.unlink()

    def test_direct_manager_review_policy(self):
        self.company.timesheet_sheet_review_policy = 'direct_manager'

        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
        })
        self.company.timesheet_sheet_review_policy = 'hr'

        sheet._compute_complete_name()

        sheet.action_timesheet_confirm()
        self.assertFalse(sheet.sudo(self.employee_user).can_review)
        self.assertEqual(
            self.HrTimesheetSheet.sudo(self.employee_user).search_count(
                [('can_review', '=', True)]
            ),
            0
        )
        with self.assertRaises(UserError):
            sheet.sudo(self.employee_user).action_timesheet_done()
        sheet.sudo(self.direct_manager_user).action_timesheet_done()
        sheet.sudo(self.direct_manager_user).action_timesheet_draft()
        sheet.unlink()

    def test_top_manager_review_policy(self):
        self.company.timesheet_sheet_review_policy = 'direct_manager'

        self.assertTrue(self.direct_manager.child_ids)
        self.assertFalse(self.direct_manager.parent_id)
        sheet = self.HrTimesheetSheet.sudo(self.direct_manager_user).create({
            'company_id': self.company.id,
        })
        sheet._compute_complete_name()
        sheet.action_timesheet_confirm()
        self.assertFalse(sheet.sudo(self.employee_user).can_review)
        self.assertTrue(sheet.sudo(self.direct_manager_user).can_review)

        with self.assertRaises(UserError):
            sheet.sudo(self.employee_user).action_timesheet_done()
        sheet.sudo(self.direct_manager_user).action_timesheet_done()
        with self.assertRaises(UserError):
            sheet.sudo(self.employee_user).action_timesheet_draft()
        sheet.sudo(self.direct_manager_user).action_timesheet_draft()
        sheet.unlink()
