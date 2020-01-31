# Copyright 2018-2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, DAILY

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError

from ..models.hr_timesheet_sheet import empty_name


class TestHrTimesheetSheet(TransactionCase):

    def setUp(self):
        super().setUp()
        officer_group = self.env.ref('hr.group_hr_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        sheet_user_group = self.env.ref('hr_timesheet.group_hr_timesheet_user')
        project_user_group = self.env.ref('project.group_project_user')
        self.sheet_model = self.env['hr_timesheet.sheet']
        self.sheet_line_model = self.env['hr_timesheet.sheet.line']
        self.project_model = self.env['project.project']
        self.task_model = self.env['project.task']
        self.aal_model = self.env['account.analytic.line']
        self.aaa_model = self.env['account.analytic.account']
        self.employee_model = self.env['hr.employee']
        self.department_model = self.env['hr.department']
        self.company = self.env['res.company'].create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
            'parent_id': self.company.id,
        })
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True
        ).create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@oca.com',
            'groups_id': [(6, 0, [
                officer_group.id,
                sheet_user_group.id,
                project_user_group.id,
                multi_company_group.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })

        self.user_2 = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True
        ).create({
            'name': 'Test User 2',
            'login': 'test_user_2',
            'email': 'test2@oca.com',
            'groups_id': [(6, 0, [
                officer_group.id,
                sheet_user_group.id,
                project_user_group.id,
                multi_company_group.id,
            ])],
            'company_id': self.company_2.id,
            'company_ids': [(4, self.company_2.id)],
        })

        self.user_3 = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True
        ).create({
            'name': 'Test User 3',
            'login': 'test_user_3',
            'email': 'test3@oca.com',
            'groups_id': [(6, 0, [
                sheet_user_group.id,
                project_user_group.id,
                multi_company_group.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })

        self.user_4 = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True
        ).create({
            'name': 'Test User 4',
            'login': 'test_user_4',
            'email': 'test4@oca.com',
            'groups_id': [(6, 0, [
                officer_group.id,
                sheet_user_group.id,
                project_user_group.id,
                multi_company_group.id,
            ])],
            'company_id': self.company.id,
            'company_ids': [(4, self.company.id)],
        })

        self.employee_manager = self.employee_model.create({
            'name': "Test Manager",
            'user_id': self.user_2.id,
            'company_id': self.user.company_id.id,
        })

        self.employee = self.employee_model.create({
            'name': "Test Employee",
            'user_id': self.user.id,
            'parent_id': self.employee_manager.id,
            'company_id': self.user.company_id.id,
        })

        self.employee_no_user = self.employee_model.create({
            'name': "Test Employee (no user)",
            'parent_id': self.employee_manager.id,
            'company_id': self.user.company_id.id,
        })

        self.department_manager = self.employee_model.create({
            'name': "Test Department Manager",
            'user_id': self.user_3.id,
            'company_id': self.user.company_id.id,
        })

        self.employee_4 = self.employee_model.create({
            'name': "Test User 4",
            'user_id': self.user_4.id,
            'parent_id': self.department_manager.id,
            'company_id': self.user.company_id.id,
        })

        self.department = self.department_model.create({
            'name': "Department test",
            'company_id': self.user.company_id.id,
        })

        self.department_2 = self.department_model.create({
            'name': "Department test 2",
            'company_id': self.user.company_id.id,
            'manager_id': self.department_manager.id,
        })

        self.project_1 = self.project_model.create({
            'name': "Project 1",
            'company_id': self.user.company_id.id,
            'allow_timesheets': True,
            'user_id': self.user_3.id,
        })
        self.project_2 = self.project_model.create({
            'name': "Project 2",
            'company_id': self.user.company_id.id,
            'allow_timesheets': True,
            'user_id': self.user_4.id,
        })
        self.task_1 = self.task_model.create({
            'name': "Task 1",
            'project_id': self.project_1.id,
            'company_id': self.user.company_id.id,
        })
        self.task_2 = self.task_model.create({
            'name': "Task 2",
            'project_id': self.project_2.id,
            'company_id': self.user.company_id.id,
        })

    def test_0(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'company_id': self.user.company_id.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertTrue(sheet.employee_id)

        sheet.add_line_project_id = self.project_1
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)

        sheet.date_end = sheet.date_end + relativedelta(days=1)
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

    def test_1(self):
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
            'review_policy': (
                self.user.company_id.timesheet_sheet_review_policy
            ),
            'state': 'new',
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        timesheet = self.aal_model.create({
            'name': 'test',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'sheet_id': sheet.id,
        })
        sheet.timesheet_ids = timesheet
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertFalse(any([l.unit_amount for l in sheet.line_ids]))
        self.assertEqual(timesheet.unit_amount, 0)

        timesheet.unit_amount = 1.0
        self.assertEqual(len(sheet.timesheet_ids), 1)
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertTrue(any([l.unit_amount for l in sheet.line_ids]))

        line = sheet.line_ids.filtered(lambda l: l.unit_amount)
        line.unit_amount = 2.0
        line.onchange_unit_amount()
        self.assertEqual(line.unit_amount, 2.0)
        self.assertEqual(timesheet.unit_amount, 1.0)

        sheet = self.sheet_model.sudo(self.user).create(
            sheet._convert_to_write(sheet._cache))
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

    def test_1_B(self):
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
            'review_policy': (
                self.user.company_id.timesheet_sheet_review_policy
            ),
            'state': 'new',
            'timesheet_ids': [(0, 0, {
                'name': empty_name,
                'date': self.sheet_model._default_date_start(),
                'project_id': self.project_1.id,
                'employee_id': self.employee.id,
                'unit_amount': 1,
            })],
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(sheet.state, 'new')

        line = self.sheet_line_model.new({
            'date': self.sheet_model._default_date_start(),
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'sheet_id': sheet.id,
            'unit_amount': 1,
        })
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(sheet.state, 'new')

        created_sheet = self.sheet_model.sudo(self.user).create(
            sheet._convert_to_write(sheet._cache))
        self.assertEqual(created_sheet.state, 'draft')

    def test_2(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'department_id': self.department.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        self.employee._compute_timesheet_sheet_count()
        self.assertEqual(self.employee.timesheet_sheet_count, 1)
        self.department._compute_timesheet_to_approve()
        self.assertEqual(self.department.timesheet_sheet_to_approve_count, 0)

        sheet.add_line_project_id = self.project_1
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        self.assertFalse(sheet.add_line_project_id.id)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)

        line = fields.first(sheet.line_ids)
        line.unit_amount = 2.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(line.unit_amount, 2.0)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        timesheet = fields.first(sheet.timesheet_ids)

        other_lines = sheet.line_ids.filtered(
            lambda l: l.date != timesheet.date)
        line2 = fields.first(other_lines)
        self.assertEqual(line2.unit_amount, 0.0)
        line2.unit_amount = 1.0
        line2.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(line2.unit_amount, 1.0)
        self.assertEqual(len(sheet.timesheet_ids), 2)

        sheet.add_line_project_id = self.project_2
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        self.assertEqual(len(sheet.timesheet_ids), 3)
        self.assertIn(timesheet.id, sheet.timesheet_ids.ids)
        self.assertEqual(len(sheet.line_ids), 7)

        self.assertEqual(sheet.state, 'draft')
        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, 'confirm')
        self.department._compute_timesheet_to_approve()
        self.assertEqual(self.department.timesheet_sheet_to_approve_count, 1)

        # Confirmed timesheet cannot be modified
        with self.assertRaises(UserError):
            timesheet.unit_amount = 0.0
        self.assertEqual(timesheet.unit_amount, 2.0)

        # Force confirmed timesheet to be modified
        timesheet.with_context(skip_check_state=True).unit_amount = 0.0
        self.assertEqual(timesheet.unit_amount, 0.0)

        with self.assertRaises(UserError):
            timesheet.unlink()
        sheet.action_timesheet_done()
        self.assertEqual(sheet.state, 'done')
        with self.assertRaises(UserError):
            sheet.unlink()
        sheet.action_timesheet_draft()
        self.assertEqual(sheet.state, 'draft')
        sheet.unlink()

    def test_3(self):
        timesheet = self.aal_model.create({
            'name': empty_name,
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
            'review_policy': (
                self.user.company_id.timesheet_sheet_review_policy
            ),
            'state': 'new',
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertTrue(self.aal_model.search([('id', '=', timesheet.id)]))

        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)

        sheet = self.sheet_model.sudo(self.user).create(
            sheet._convert_to_write(sheet._cache))
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertFalse(self.aal_model.search([('id', '=', timesheet.id)]))

    def test_4(self):
        timesheet_1 = self.aal_model.create({
            'name': empty_name,
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })
        timesheet_2 = self.aal_model.create({
            'name': empty_name,
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 1.0,
        })
        timesheet_3 = self.aal_model.create({
            'name': 'x',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })
        # With this we assure to be in the same week but different day
        # (for covering today = sunday)
        days = -1 if timesheet_3.date.weekday() == 6 else 1
        timesheet_3.date = timesheet_3.date + relativedelta(days=days)

        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertEqual(len(timesheet_1_or_2), 1)
        self.assertEqual(timesheet_1_or_2.unit_amount, 1.0)
        self.assertEqual(timesheet_3.unit_amount, 0.0)

        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 1.0)
        line.unit_amount = 0.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(line.unit_amount, 0.0)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertFalse(self.aal_model.search(
            [('id', '=', timesheet_1_or_2.id)]))

        timesheet_3.name = empty_name
        sheet._onchange_timesheets()
        sheet.add_line_project_id = self.project_2
        sheet.onchange_add_project_id()
        sheet.add_line_task_id = self.task_2
        sheet.sudo(self.user).button_add_line()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertFalse(self.aal_model.search(
            [('id', '=', timesheet_3.id)]))

    def test_5(self):
        timesheet_1 = self.aal_model.create({
            'name': empty_name,
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        timesheet_2 = self.aal_model.create({
            'name': 'x',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 4.0)

        timesheet_2.name = empty_name
        sheet._onchange_timesheets()
        line.unit_amount = 3.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(fields.first(sheet.timesheet_ids).unit_amount, 3.0)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertEqual(len(timesheet_1_or_2), 1)
        self.assertEqual(timesheet_1_or_2.unit_amount, 3.0)

        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        line.unit_amount = 4.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(fields.first(sheet.timesheet_ids).unit_amount, 4.0)
        self.assertEqual(timesheet_1_or_2.unit_amount, 4.0)

        line.unit_amount = -1.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)

    def test_6(self):
        timesheet_1 = self.aal_model.create({
            'name': empty_name,
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        timesheet_2 = self.aal_model.create({
            'name': 'w',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        timesheet_3 = self.aal_model.create({
            'name': 'x',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        timesheet_4 = self.aal_model.create({
            'name': 'y',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        timesheet_5 = self.aal_model.create({
            'name': 'z',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 5)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 10.0)

        timesheet_2.name = empty_name
        sheet._onchange_timesheets()
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        line.unit_amount = 6.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(len(sheet.timesheet_ids), 3)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertFalse(timesheet_1_or_2)

        line.unit_amount = 3.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(len(sheet.timesheet_ids), 4)
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 4)
        self.assertEqual(line.unit_amount, 3.0)

        timesheet_3_4_and_5 = self.aal_model.search(
            [('id', 'in', [timesheet_3.id, timesheet_4.id, timesheet_5.id])])
        self.assertEqual(len(timesheet_3_4_and_5), 3)

        timesheet_6 = self.aal_model.create({
            'name': 'z',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        timesheet_5.name = empty_name
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 4)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 5.0)

        line.unit_amount = 1.0
        line.onchange_unit_amount()
        self.assertEqual(len(sheet.new_line_ids), 1)
        new_line = fields.first(sheet.new_line_ids)
        sheet.write({
            'line_ids': [(1, 0, {'new_line_id': new_line.id})]
        })
        self.assertEqual(len(sheet.timesheet_ids), 4)
        self.assertTrue(timesheet_6.exists().ids)

    def test_end_date_before_start_date(self):
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'date_start': self.sheet_model._default_date_end(),
            'date_end': self.sheet_model._default_date_start(),
            'review_policy': (
                self.user.company_id.timesheet_sheet_review_policy
            ),
            'state': 'new',
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        with self.assertRaises(ValidationError):
            self.sheet_model.sudo(self.user).create(
                sheet._convert_to_write(sheet._cache))

    def test_no_copy(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        sheet._onchange_scope()
        with self.assertRaises(UserError):
            sheet.sudo(self.user).copy()

    def test_no_overlap(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        sheet._onchange_scope()
        with self.assertRaises(ValidationError):
            self.sheet_model.sudo(self.user).create({
                'employee_id': self.employee.id,
                'company_id': self.user.company_id.id,
            })

    def test_8(self):
        """Multicompany test"""
        employee_2 = self.employee_model.create({
            'name': "Test User 2",
            'user_id': self.user_2.id,
            'company_id': self.user_2.company_id.id,
        })
        department_2 = self.department_model.create({
            'name': "Department test 2",
            'company_id': self.user_2.company_id.id,
        })
        project_3 = self.project_model.create({
            'name': "Project 3",
            'company_id': self.user_2.company_id.id,
        })
        task_3 = self.task_model.create({
            'name': "Task 3",
            'project_id': project_3.id,
            'company_id': self.user_2.company_id.id,
        })
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'department_id': self.department.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        with self.assertRaises(ValidationError):
            sheet.company_id = self.user_2.company_id.id
        sheet.company_id = self.user.company_id.id
        with self.assertRaises(ValidationError):
            sheet.employee_id = employee_2
        with self.assertRaises(ValidationError):
            sheet.department_id = department_2
        with self.assertRaises(ValidationError):
            sheet.add_line_project_id = project_3
        with self.assertRaises(ValidationError):
            sheet.add_line_task_id = task_3

    def test_9(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'department_id': self.department.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        sheet.add_line_project_id = self.project_1
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        self.assertEqual(len(sheet.timesheet_ids), 1)

        with self.assertRaises(UserError):
            sheet.action_timesheet_refuse()

        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, 'confirm')

        sheet.action_timesheet_refuse()
        self.assertEqual(sheet.state, 'draft')

        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, 'confirm')

        sheet.action_timesheet_done()
        self.assertEqual(sheet.state, 'done')
        with self.assertRaises(UserError):
            sheet.unlink()

        sheet.action_timesheet_draft()
        self.assertEqual(sheet.state, 'draft')
        sheet.unlink()

    def test_10_start_day(self):
        """Test that the start day can be configured for weekly timesheets."""
        self.company.timesheet_week_start = '6'
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.company.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        weekday_from = sheet.date_start.weekday()
        weekday_to = sheet.date_end.weekday()

        self.assertEqual(weekday_from, 6, "The timesheet should start on "
                                          "Sunday")
        self.assertEqual(weekday_to, 5, "The timesheet should end on Saturday")

    def test_11_onchange_unit_amount(self):
        """Test onchange unit_amount for line without sheet_id."""
        self.aal_model.create({
            'name': 'test1',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
            'date': self.sheet_model._default_date_start(),
        })
        self.aal_model.create({
            'name': 'test2',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
            'date': self.sheet_model._default_date_start(),
        })
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'department_id': self.department.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
            'state': 'new',
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 2)
        self.assertEqual(len(sheet.line_ids), 7)

        unit_amount = 0.0
        for line in sheet.line_ids:
            if line.unit_amount:
                line.sheet_id = False
                unit_amount = line.unit_amount
                line.write({'unit_amount': unit_amount + 1.0})
                res_onchange = line.with_context(
                    params={'model': 'hr_timesheet.sheet', 'id': sheet.id}
                ).onchange_unit_amount()
                self.assertFalse(res_onchange)
                self.assertEqual(line.unit_amount, unit_amount + 1.0)

        self.assertEqual(len(sheet.timesheet_ids), 2)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.new_line_ids), 1)

        new_line = fields.first(sheet.new_line_ids)
        self.assertEqual(new_line.unit_amount, unit_amount + 1.0)

        for line in sheet.line_ids:
            if line.unit_amount:
                line.sheet_id = False
                unit_amount = line.unit_amount
                line.write({'unit_amount': unit_amount + 1.0})
                res_onchange = line.onchange_unit_amount()
                warning = res_onchange.get('warning')
                self.assertTrue(warning)
                message = warning.get('message')
                self.assertTrue(message)

    def test_12_creating_sheet(self):
        """Test onchange unit_amount for line without sheet_id."""
        self.aal_model.create({
            'name': 'test1',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
            'date': self.sheet_model._default_date_start(),
        })
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'department_id': self.department.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

        line = sheet.line_ids.filtered(lambda l: l.unit_amount)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 2.0)

        unit_amount = line.unit_amount
        line.write({'unit_amount': unit_amount})
        line.onchange_unit_amount()
        self.assertEqual(line.unit_amount, 2.0)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

    def test_13(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'company_id': self.user.company_id.id,
        })

        self.assertIsNotNone(sheet.name)

        sheet.date_end = sheet.date_start + relativedelta(years=1)
        self.assertIsNotNone(sheet.name)

    def test_14_analytic_account_multicompany(self):
        new_employee = self.employee_model.create({
            'name': "Test New Employee",
            'user_id': self.user_2.id,
            'company_id': self.company_2.id,
        })
        sheet = self.sheet_model.sudo(self.user_2).create({
            'employee_id': new_employee.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
        })
        self.assertEqual(sheet.company_id, self.company_2)

        timesheet_1 = self.aal_model.create({
            'name': 'test1',
            'project_id': self.project_1.id,
            'employee_id': new_employee.id,
            'unit_amount': 1.0,
            'date': self.sheet_model._default_date_start(),
        })
        with self.assertRaises(ValidationError):
            timesheet_1.write({
                'sheet_id': sheet.id,
            })

        new_project = self.project_model.create({
            'name': "Project Test",
            'company_id': self.company_2.id,
            'allow_timesheets': True,
        })
        timesheet_2 = self.aal_model.create({
            'name': 'test1',
            'project_id': new_project.id,
            'employee_id': new_employee.id,
            'unit_amount': 1.0,
            'date': self.sheet_model._default_date_start(),
        })
        timesheet_2.write({
            'sheet_id': sheet.id,
        })

    def test_15(self):
        """Test company constraint in Account Analytic Account."""
        self.aal_model.create({
            'name': 'test1',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'company_id': self.company.id,
            'unit_amount': 2.0,
            'date': self.sheet_model._default_date_start(),
        })
        self.assertNotEqual(self.company, self.company_2)
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'department_id': self.department.id,
        })
        self.assertEqual(sheet.company_id, self.company)
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(sheet.timesheet_ids.company_id, self.company)

        analytic_account = sheet.timesheet_ids.account_id
        self.assertEqual(analytic_account.company_id, self.company)

        with self.assertRaises(ValidationError):
            analytic_account.company_id = self.company_2

    def test_16(self):
        department = self.department_model.create({
            'name': "Department test",
            'company_id': False,
        })
        new_employee = self.employee_model.create({
            'name': "Test User",
            'user_id': self.user.id,
            'company_id': False,
            'department_id': department.id,
        })
        self.assertFalse(new_employee.company_id)
        sheet_no_department = self.sheet_model.sudo(self.user).create({
            'employee_id': new_employee.id,
            'department_id': False,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
        })
        self.assertFalse(sheet_no_department.department_id)
        sheet_no_department._onchange_employee_id()
        self.assertTrue(sheet_no_department.department_id)
        self.assertEqual(sheet_no_department.department_id, department)
        self.assertTrue(sheet_no_department.company_id)

        sheet_no_department.unlink()
        sheet_no_employee = self.sheet_model.sudo(self.user).create({
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
        })
        self.assertTrue(sheet_no_employee.employee_id)
        self.assertFalse(sheet_no_employee.department_id)
        sheet_no_employee._onchange_employee_id()
        self.assertFalse(sheet_no_employee.department_id)
        self.assertTrue(sheet_no_employee.company_id)

    def test_sheet_range_monthly(self):
        self.company.sheet_range = MONTHLY
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.company.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        sheet._compute_name()
        self.assertEqual(sheet.date_start.day, 1)
        self.assertEqual(sheet.date_start.month, sheet.date_end.month)

    def test_sheet_range_daily(self):
        self.company.sheet_range = DAILY
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.company.id,
        })
        sheet._onchange_scope()
        sheet._onchange_timesheets()
        sheet._compute_name()
        self.assertEqual(sheet.date_start, sheet.date_end)

    def test_employee_no_user(self):
        with self.assertRaises(UserError):
            self.sheet_model.sudo(self.user).create({
                'employee_id': self.employee_no_user.id,
                'company_id': self.company.id,
            })

        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.company.id,
        })
        with self.assertRaises(UserError):
            sheet.employee_id = self.employee_no_user

    def test_workflow(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'company_id': self.user.company_id.id,
        })

        self.sheet_model.sudo(self.user).fields_view_get(view_type='form')
        self.sheet_model.sudo(self.user).fields_view_get(view_type='tree')

        with self.assertRaises(UserError):
            sheet.sudo(self.user_3).action_timesheet_refuse()
        with self.assertRaises(UserError):
            sheet.sudo(self.user_3).action_timesheet_done()

        sheet.action_timesheet_confirm()
        self.assertFalse(sheet.sudo(self.user_3).can_review)
        self.assertEqual(
            self.sheet_model.sudo(self.user_3).search_count(
                [('can_review', '=', True)]
            ),
            0
        )
        self.assertEqual(
            self.sheet_model.sudo(self.user_3).search_count(
                [('can_review', '!=', False)]
            ),
            0
        )
        self.assertEqual(
            self.sheet_model.sudo(self.user_3).search_count(
                [('can_review', '=', False)]
            ),
            1
        )
        self.assertEqual(
            self.sheet_model.sudo(self.user_3).search_count(
                [('can_review', '!=', True)]
            ),
            1
        )
        with self.assertRaises(UserError):
            sheet.sudo(self.user_3).action_timesheet_draft()
        sheet.action_timesheet_done()
        sheet.action_timesheet_draft()
        sheet.unlink()

    def test_review_policy_default(self):
        self.assertEqual(
            self.company.timesheet_sheet_review_policy,
            'hr'
        )
        sheet = self.sheet_model.sudo(self.user).create({
            'company_id': self.user.company_id.id,
        })
        self.assertEqual(sheet.review_policy, 'hr')
        sheet.unlink()

    def test_same_week_different_years(self):
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'date_start': date(2019, 12, 30),
            'date_end': date(2020, 1, 5),
        })
        self.assertEqual(sheet.name, 'Week 01, 2020')

    def test_different_weeks_different_years(self):
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'date_start': date(2019, 12, 29),
            'date_end': date(2020, 1, 5),
        })
        self.assertEqual(sheet.name, 'Weeks 52, 2019 - 01, 2020')
