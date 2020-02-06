# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import common


class TestHrTimesheetSheetPolicyDepartmentManager(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.ResCompany = self.env['res.company']
        self.ResUsers = self.env['res.users']
        self.HrTimesheetSheet = self.env['hr_timesheet.sheet']
        self.HrEmployee = self.env['hr.employee']
        self.HrDepartment = self.env['hr.department']

        self.group_hr_user = self.env.ref('hr.group_hr_user')
        self.group_multi_company = self.env.ref('base.group_multi_company')
        self.group_hr_timesheet_user = self.env.ref(
            'hr_timesheet.group_hr_timesheet_user'
        )
        self.group_project_user = self.env.ref('project.group_project_user')

        self.company = self.ResCompany.create({
            'name': 'Company',
        })
        self.env.user.company_ids += self.company
        self.department_manager_user = self.ResUsers.with_context({
            'no_reset_password': True,
        }).create({
            'name': 'Department Manager User',
            'login': 'department_manager_user',
            'email': 'department_manager_user@example.com',
            'groups_id': [(6, 0, [
                self.group_hr_timesheet_user.id,
                self.group_project_user.id,
                self.group_multi_company.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })
        self.employee_user = self.ResUsers.with_context({
            'no_reset_password': True,
        }).create({
            'name': 'Employee User',
            'login': 'employee_user',
            'email': 'employee_user@example.com',
            'groups_id': [(6, 0, [
                self.group_hr_user.id,
                self.group_hr_timesheet_user.id,
                self.group_project_user.id,
                self.group_multi_company.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })
        self.employee = self.HrEmployee.create({
            'name': 'Employee',
            'user_id': self.employee_user.id,
            'company_id': self.company.id,
        })
        self.department_manager = self.HrEmployee.create({
            'name': 'Department Manager',
            'user_id': self.department_manager_user.id,
            'company_id': self.company.id,
        })
        self.department = self.HrDepartment.create({
            'name': 'Department',
            'company_id': self.company.id,
            'manager_id': self.department_manager.id,
        })

    def test_review_policy_capture(self):
        self.company.timesheet_sheet_review_policy = 'department_manager'
        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
            'department_id': self.department.id,
        })
        self.assertEqual(sheet.review_policy, 'department_manager')
        self.company.timesheet_sheet_review_policy = 'hr'
        self.assertEqual(sheet.review_policy, 'department_manager')
        sheet.unlink()

    def test_department_manager_review_policy(self):
        self.company.timesheet_sheet_review_policy = 'department_manager'

        self.HrTimesheetSheet.sudo(self.employee_user).fields_view_get(
            view_type='form',
        )
        self.HrTimesheetSheet.sudo(self.employee_user).fields_view_get(
            view_type='tree',
        )

        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
            'department_id': self.department.id,
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
        sheet.sudo(self.department_manager_user).action_timesheet_done()
        sheet.sudo(self.department_manager_user).action_timesheet_draft()
        sheet.unlink()
