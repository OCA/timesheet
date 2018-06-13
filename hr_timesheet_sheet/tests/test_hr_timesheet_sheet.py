# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo import fields
from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestHrTimesheetSheet(TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheet, self).setUp()
        employees_group = self.env.ref('base.group_user')
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
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   sheet_user_group.id,
                                   project_user_group.id,
                                   multi_company_group.id,
                                   ])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })

        self.user_2 = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User 2',
             'login': 'test_user_2',
             'email': 'test2@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   sheet_user_group.id,
                                   project_user_group.id,
                                   multi_company_group.id,
                                   ])],
             'company_id': self.company_2.id,
             'company_ids': [(4, self.company_2.id)],
             })

        self.employee = self.employee_model.create({
            'name': "Test User",
            'user_id': self.user.id,
            'company_id': self.user.company_id.id,
        })

        self.department = self.department_model.create({
            'name': "Department test",
            'company_id': self.user.company_id.id,
        })

        self.project_1 = self.project_model.create({
            'name': "Project 1",
            'company_id': self.user.company_id.id,
        })
        self.project_2 = self.project_model.create({
            'name': "Project 2",
            'company_id': self.user.company_id.id,
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

    def test_1(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        sheet.add_line_project_id = self.project_1
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

        sheet.date_end = fields.Date.to_string(
            fields.Date.from_string(sheet.date_end) + relativedelta(days=1))
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

    def test_2(self):
        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'department_id': self.department.id,
        })
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        self.employee._compute_timesheet_count()
        self.assertEqual(self.employee.timesheet_count, 1)
        self.department._compute_timesheet_to_approve()
        self.assertEqual(self.department.timesheet_sheet_to_approve_count, 0)

        sheet.add_line_project_id = self.project_1
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        sheet._onchange_dates_or_timesheets()
        sheet.onchange_add_project_id()
        self.assertEqual(sheet.add_line_project_id.id, False)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        timesheet = sheet.timesheet_ids[0]

        line = sheet.line_ids.filtered(lambda l: l.date != timesheet.date)[0]
        self.assertEqual(line.unit_amount, 0.0)
        self.assertEqual(line.count_timesheets, 0)
        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 1.0}, update=True))
        line.onchange_unit_amount()
        self.assertEqual(line.unit_amount, 1.0)
        self.assertEqual(line.count_timesheets, 1)
        self.assertEqual(len(sheet.timesheet_ids), 2)

        sheet.add_line_project_id = self.project_2
        sheet.onchange_add_project_id()
        sheet.sudo(self.user).button_add_line()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 2)
        self.assertNotIn(timesheet.id, sheet.timesheet_ids.ids)
        self.assertEqual(len(sheet.line_ids), 14)
        timesheet = sheet.timesheet_ids.filtered(
            lambda t: t.unit_amount != 0.0)

        self.assertEqual(sheet.state, 'draft')
        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, 'confirm')
        self.department._compute_timesheet_to_approve()
        self.assertEqual(self.department.timesheet_sheet_to_approve_count, 1)
        with self.assertRaises(UserError):
            timesheet.unit_amount = 0.0
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
            'name': '/',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'date_start': self.sheet_model._default_date_start(),
            'date_end': self.sheet_model._default_date_end(),
        })
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertTrue(self.aal_model.search([('id', '=', timesheet.id)]))

        sheet = self.sheet_model.sudo(self.user).create(
            sheet._convert_to_write(sheet._cache))
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertFalse(self.aal_model.search([('id', '=', timesheet.id)]))

    def test_4(self):
        timesheet_1 = self.aal_model.create({
            'name': '/',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })
        timesheet_2 = self.aal_model.create({
            'name': '/',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 1.0,
        })
        timesheet_3 = self.aal_model.create({
            'name': 'x',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
        })
        timesheet_3.date = fields.Date.to_string(
            fields.Date.from_string(timesheet_3.date) + relativedelta(days=1))

        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertEqual(len(timesheet_1_or_2), 1)
        self.assertEqual(timesheet_1_or_2.unit_amount, 1.0)
        self.assertEqual(timesheet_3.unit_amount, 0.0)

        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.count_timesheets, 1)
        self.assertEqual(line.unit_amount, 1.0)
        line.unit_amount = 0.0
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertFalse(self.aal_model.search(
            [('id', '=', timesheet_1_or_2.id)]))

        timesheet_3.name = '/'
        sheet.add_line_project_id = self.project_2
        sheet.onchange_add_project_id()
        sheet.add_line_task_id = self.task_2
        sheet.sudo(self.user).button_add_line()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertFalse(self.aal_model.search(
            [('id', '=', timesheet_3.id)]))

    def test_5(self):
        timesheet_1 = self.aal_model.create({
            'name': '/',
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
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.count_timesheets, 2)
        self.assertEqual(line.unit_amount, 4.0)

        timesheet_2.name = '/'
        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 3.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(sheet.timesheet_ids[0].unit_amount, 3.0)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertEqual(len(timesheet_1_or_2), 1)
        self.assertEqual(timesheet_1_or_2.unit_amount, 3.0)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 4.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(line.count_timesheets, 1)
        self.assertEqual(sheet.timesheet_ids[0].unit_amount, 4.0)
        self.assertEqual(timesheet_1_or_2.unit_amount, 4.0)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': -1.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(len(sheet.timesheet_ids), 0)

    def test_6(self):
        timesheet_1 = self.aal_model.create({
            'name': '/',
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
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 5)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.count_timesheets, 5)
        self.assertEqual(line.unit_amount, 10.0)

        timesheet_2.name = '/'
        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 6.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 3)
        self.assertEqual(line.count_timesheets, 3)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertFalse(timesheet_1_or_2)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 3.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 3)
        self.assertEqual(line.count_timesheets, 3)

        timesheet_3_4_and_5 = self.aal_model.search(
            [('id', 'in', [timesheet_3.id, timesheet_4.id, timesheet_5.id])])
        self.assertEqual(len(timesheet_3_4_and_5), 3)

        timesheet_6 = self.aal_model.create({
            'name': '/',
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 4)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.count_timesheets, 4)
        self.assertEqual(line.unit_amount, 5.0)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 1.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 3)
        self.assertEqual(line.count_timesheets, 3)
        self.assertFalse(self.aal_model.search([('id', '=', timesheet_6.id)]))

    def test_7(self):
        sheet = self.sheet_model.sudo(self.user).new({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
            'date_start': self.sheet_model._default_date_end(),
            'date_end': self.sheet_model._default_date_start(),
        })
        sheet._onchange_dates_or_timesheets()
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        with self.assertRaises(ValidationError):
            self.sheet_model.sudo(self.user).create(
                sheet._convert_to_write(sheet._cache))

        sheet = self.sheet_model.sudo(self.user).create({
            'employee_id': self.employee.id,
            'company_id': self.user.company_id.id,
        })
        with self.assertRaises(UserError):
            sheet.sudo(self.user).copy()
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
