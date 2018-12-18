# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestHrTimesheetReport(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.IrActionReport = self.env['ir.actions.report']
        self.Project = self.env['project.project']
        self.HrEmployee = self.env['hr.employee']
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.Wizard = self.env['hr.timesheet.report.wizard']
        self.Report = self.env['hr.timesheet.report']

    def test_multi_project(self):
        project_1 = self.Project.create({
            'name': 'Project 1',
        })
        project_2 = self.Project.create({
            'name': 'Project 2',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        entry_1 = self.AccountAnalyticLine.create({
            'project_id': project_1.id,
            'name': 'Time Entry 1',
            'employee_id': employee.id,
            'date': self.today,
            'unit_amount': 1,
        })
        entry_2 = self.AccountAnalyticLine.create({
            'project_id': project_2.id,
            'name': 'Time Entry 2',
            'employee_id': employee.id,
            'date': self.today,
            'unit_amount': 2,
        })

        entries = self.AccountAnalyticLine
        entries |= entry_1
        entries |= entry_2

        entries.action_timesheet_report_wizard()

        wizard = self.Wizard.create({
            'date_from': self.today,
            'date_to': self.today,
            'employee_ids': [(6, False, [employee.id])],
            'grouping_field_ids': self.Wizard._default_grouping_field_ids(),
            'entry_field_ids': self.Wizard._default_entry_field_ids(),
        })
        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.assertEqual(len(report.group_ids), 2)
        self.assertEqual(report.total_unit_amount, 3)

    def test_html_export(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'date': self.today,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'employee_ids': [(6, False, [employee.id])],
            'entry_field_ids': self.Wizard._default_entry_field_ids(),
        })
        wizard.action_export_html()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_timesheet_report.report'
        ).render_qweb_html(report.ids)

    def test_pdf_export(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'date': self.today,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'employee_ids': [(6, False, [employee.id])],
            'entry_field_ids': self.Wizard._default_entry_field_ids(),
        })
        wizard.action_export_pdf()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_timesheet_report.report'
        ).render_qweb_pdf(report.ids)

    def test_xlsx_export(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'date': self.today,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'employee_ids': [(6, False, [employee.id])],
            'entry_field_ids': self.Wizard._default_entry_field_ids(),
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_timesheet_report.report'
        ).render_xlsx(report.ids, None)

    def test_no_grouping(self):
        project = self.Project.create({
            'name': 'Project',
        })
        employee = self.HrEmployee.create({
            'name': 'Employee',
        })
        self.AccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry',
            'employee_id': employee.id,
            'date': self.today,
            'unit_amount': 1,
        })

        wizard = self.Wizard.create({
            'date_from': self.today,
            'date_to': self.today,
            'employee_ids': [(6, False, [employee.id])],
            'grouping_field_ids': [(5, False, False)],
            'entry_field_ids': self.Wizard._default_entry_field_ids(),
        })
        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.assertEqual(len(report.group_ids), 1)
        self.assertEqual(report.total_unit_amount, 1)
