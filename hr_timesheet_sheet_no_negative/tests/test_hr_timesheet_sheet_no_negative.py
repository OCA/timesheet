# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0
from odoo.tests.common import TransactionCase

from odoo.addons.hr_timesheet_sheet.models.hr_timesheet_sheet import empty_name


class TestHrTimesheetSheetNoNegative(TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheetNoNegative, self).setUp()
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
            'timesheet_negative_unit_amount': False,
        })

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
            'allow_timesheets': True,
        })
        self.project_2 = self.project_model.create({
            'name': "Project 2",
            'company_id': self.user.company_id.id,
            'allow_timesheets': True,
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
        sheet._onchange_dates()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 4.0)

        timesheet_2.name = empty_name
        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 3.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_timesheets()
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
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(sheet.timesheet_ids[0].unit_amount, 4.0)
        self.assertEqual(timesheet_1_or_2.unit_amount, 4.0)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': -1.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 0)

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
        sheet._onchange_dates()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 5)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 10.0)

        timesheet_2.name = empty_name
        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 6.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 3)

        timesheet_1_or_2 = self.aal_model.search(
            [('id', 'in', [timesheet_1.id, timesheet_2.id])])
        self.assertFalse(timesheet_1_or_2)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 3.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 3)
        self.assertEqual(line.unit_amount, 3.0)

        timesheet_3_4_and_5 = self.aal_model.search(
            [('id', 'in', [timesheet_3.id, timesheet_4.id, timesheet_5.id])])
        self.assertEqual(len(timesheet_3_4_and_5), 3)

        timesheet_6 = self.aal_model.create({
            'name': empty_name,
            'project_id': self.project_1.id,
            'employee_id': self.employee.id,
            'unit_amount': 2.0,
        })
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 4)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 8.0)

        line._cache.update(
            line._convert_to_cache(
                {'unit_amount': 1.0}, update=True))
        line.onchange_unit_amount()
        sheet._onchange_timesheets()
        self.assertEqual(len(sheet.timesheet_ids), 4)
        self.assertTrue(self.aal_model.search([('id', '=', timesheet_6.id)]))
