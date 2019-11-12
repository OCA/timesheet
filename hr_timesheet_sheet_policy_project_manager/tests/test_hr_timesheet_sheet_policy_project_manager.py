# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests import common


class TestHrTimesheetSheetPolicyProjectManager(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.ResUsers = self.env['res.users']
        self.ResCompany = self.env['res.company']
        self.HrEmployee = self.env['hr.employee']
        self.HrDepartment = self.env['hr.department']
        self.ProjectProject = self.env['project.project']
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.HrTimesheetSheet = self.env['hr_timesheet.sheet']
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
        self.project_manager_user_1 = self.ResUsers.with_context({
            'no_reset_password': True,
        }).create({
            'name': 'Project Manager User 1',
            'login': 'project_manager_user_1',
            'email': 'project_manager_user_1@example.com',
            'groups_id': [(6, 0, [
                self.group_hr_timesheet_user.id,
                self.group_project_user.id,
                self.group_multi_company.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })
        self.project_manager_user_2 = self.ResUsers.with_context({
            'no_reset_password': True,
        }).create({
            'name': 'Project Manager User 2',
            'login': 'project_manager_user_2',
            'email': 'project_manager_user_2@example.com',
            'groups_id': [(6, 0, [
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
        self.project_manager_1 = self.HrEmployee.create({
            'name': 'Project Manager 1',
            'user_id': self.project_manager_user_1.id,
            'company_id': self.company.id,
        })
        self.project_manager_2 = self.HrEmployee.create({
            'name': 'Project Manager 2',
            'user_id': self.project_manager_user_2.id,
            'company_id': self.company.id,
        })
        self.project_1 = self.ProjectProject.create({
            'name': 'Project 1',
            'company_id': self.company.id,
            'allow_timesheets': True,
            'user_id': self.project_manager_user_1.id,
        })
        self.project_2 = self.ProjectProject.create({
            'name': 'Project 2',
            'company_id': self.company.id,
            'allow_timesheets': True,
            'user_id': self.project_manager_user_2.id,
        })

    def test_review_policy_capture(self):
        self.company.timesheet_sheet_review_policy = 'project_manager'
        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
            'project_id': self.project_1.id,
        })
        self.assertEqual(sheet.review_policy, 'project_manager')
        self.company.timesheet_sheet_review_policy = 'hr'
        self.assertEqual(sheet.review_policy, 'project_manager')
        sheet.unlink()

    def test_project_manager_review_policy(self):
        self.company.timesheet_sheet_review_policy = 'project_manager'

        timesheet_0 = self.AccountAnalyticLine.sudo(
            self.employee_user
        ).create({
            'name': 'test',
            'project_id': self.project_2.id,
            'employee_id': self.employee.id,
        })
        timesheet_1 = self.AccountAnalyticLine.sudo(
            self.employee_user
        ).create({
            'name': 'test',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })

        with self.assertRaises(UserError):
            self.HrTimesheetSheet.sudo(self.employee_user).create({
                'company_id': self.employee_user.company_id.id,
            })
        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.employee_user.company_id.id,
            'project_id': self.project_1.id,
        })
        with self.assertRaises(UserError):
            sheet.project_id = False
        self.company.timesheet_sheet_review_policy = 'hr'

        sheet._compute_complete_name()

        sheet._onchange_project_id()
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

        with self.assertRaises(UserError):
            sheet.sudo(self.project_manager_user_2).action_timesheet_done()

        with self.assertRaises(UserError):
            sheet.sudo(self.project_manager_user_2).action_timesheet_draft()

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
        sheet.sudo(self.project_manager_user_1).action_timesheet_done()
        sheet.sudo(self.project_manager_user_1).action_timesheet_draft()
        sheet.unlink()

        timesheet_0.unlink()
        timesheet_1.unlink()

    def test_project_manager_review_policy_project_required(self):
        sheet = self.HrTimesheetSheet.sudo(self.employee_user).new({
            'employee_id': self.employee.id,
            'company_id': self.company.id,
            'date_start': self.HrTimesheetSheet._default_date_start(),
            'date_end': self.HrTimesheetSheet._default_date_end(),
            'review_policy': 'project_manager',
            'state': 'new',
        })
        values = sheet._convert_to_write(sheet._cache)
        with self.assertRaises(UserError):
            self.HrTimesheetSheet.sudo(self.employee_user).create(values)
        sheet.project_id = self.project_1
        values.update(sheet._convert_to_write(sheet._cache))
        sheet = self.HrTimesheetSheet.sudo(self.employee_user).create(values)
        with self.assertRaises(UserError):
            sheet.project_id = False
        sheet.unlink()

    def test_project_manager_review_policy_overlapping(self):
        self.company.timesheet_sheet_review_policy = 'project_manager'

        sheet1 = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
            'project_id': self.project_1.id,
        })
        with self.assertRaises(ValidationError):
            sheet2 = self.HrTimesheetSheet.sudo(self.employee_user).create({
                'company_id': self.company.id,
                'project_id': self.project_1.id,
            })

        sheet2 = self.HrTimesheetSheet.sudo(self.employee_user).create({
            'company_id': self.company.id,
            'project_id': self.project_2.id,
        })
        with self.assertRaises(ValidationError):
            sheet2.write({
                'project_id': self.project_1.id,
            })

        self.company.timesheet_sheet_review_policy = 'hr'

        sheet1.unlink()
        sheet2.unlink()
