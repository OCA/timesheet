# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError

from datetime import date
from dateutil.relativedelta import relativedelta


class TestHrUtilizationReport(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.wednesday = date(2018, 2, 6)
        self.saturday = date(2018, 2, 2)
        self.IrActionReport = self.env['ir.actions.report']
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.Wizard = self.env['hr.utilization.report.wizard']
        self.Report = self.env['hr.utilization.report']

    def test_1(self):
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #1-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #1-2',
            'active': False,
        })
        employee_3 = self.SudoHrEmployee.create({
            'name': 'Employee #1-3',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #1-1',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 4,
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #1-2',
            'employee_id': employee_1.id,
            'date': self.wednesday - relativedelta(days=1),
            'unit_amount': 4,
        })

        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
                employee_3.id,
            ])],
        })

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.assertEqual(len(report.group_ids), 1)
        self.assertEqual(len(report.group_ids[0].block_ids), 2)
        self.assertEqual(report.total_unit_amount_a, 4.0)
        self.assertEqual(report.total_utilization_a, 0.25)
        self.assertEqual(report.total_unit_amount_b, 0.0)
        self.assertEqual(report.total_utilization_b, 0.0)

    def test_2(self):
        project = self.SudoProject.create({
            'name': 'Project #2',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #2-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #2-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #2',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
        })
        wizard.action_export_html()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_qweb_html(report.ids)

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #3-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #3-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #3',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
        })
        wizard.action_export_pdf()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_qweb_pdf(report.ids)

    def test_4(self):
        project = self.SudoProject.create({
            'name': 'Project #4',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #4-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #4-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #4',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
            'utilization_format': 'percentage',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_5(self):
        project = self.SudoProject.create({
            'name': 'Project #5',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #5-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #5-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #5',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
            'utilization_format': 'absolute',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_6(self):
        project = self.SudoProject.create({
            'name': 'Project #6',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #6-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #6-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #6',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })
        selection_split_by_field_name = (
            self.Wizard._selection_split_by_field_name()
        )
        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
            'split_by_field_name': (
                selection_split_by_field_name[0][0]
                if selection_split_by_field_name
                else None
            ),
            'utilization_format': 'percentage',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_7(self):
        project = self.SudoProject.create({
            'name': 'Project #7',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #7-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #7-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #7',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })
        selection_split_by_field_name = (
            self.Wizard._selection_split_by_field_name()
        )
        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
            'split_by_field_name': (
                selection_split_by_field_name[0][0]
                if selection_split_by_field_name
                else None
            ),
            'utilization_format': 'absolute',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_8(self):
        project = self.SudoProject.create({
            'name': 'Project #8',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #8-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #8-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #8',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 4,
        })

        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'date_from': self.wednesday,
                'date_to': self.wednesday,
                'employee_ids': [(6, False, [
                    employee_1.id,
                    employee_2.id,
                ])],
                'grouping_field_ids': [(0, False, {
                    'sequence': 10,
                    'field_name': 'department_id',
                })],
                'entry_field_ids': [(0, False, {
                    'sequence': 10,
                    'field_name': 'project_id',
                })],
            })

    def test_9(self):
        project = self.SudoProject.create({
            'name': 'Project #9',
        })
        employee_1 = self.SudoHrEmployee.create({
            'name': 'Employee #9-1',
        })
        employee_2 = self.SudoHrEmployee.create({
            'name': 'Employee #9-2',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #9',
            'employee_id': employee_1.id,
            'date': self.wednesday,
            'unit_amount': 4,
        })

        self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee_1.id,
                employee_2.id,
            ])],
            'grouping_field_ids': [(6, False, [])],
        })

        with self.assertRaises(ValidationError):
            self.Wizard.create({
                'date_from': self.wednesday,
                'date_to': self.wednesday,
                'employee_ids': [(6, False, [
                    employee_1.id,
                    employee_2.id,
                ])],
                'entry_field_ids': [(6, False, [])],
            })

    def test_10(self):
        project = self.SudoProject.create({
            'name': 'Project #10',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #10',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #10',
            'employee_id': employee.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })

        self.assertIn(
            'group_id',
            map(
                lambda x: x[0],
                self.Wizard._selection_split_by_field_name()
            )
        )

        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee.id,
            ])],
            'split_by_field_name': 'group_id',
            'utilization_format': 'percentage',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_11(self):
        project = self.SudoProject.create({
            'name': 'Project #11',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #11',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #11',
            'employee_id': employee.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })

        self.assertIn(
            'tag_ids',
            map(
                lambda x: x[0],
                self.Wizard._selection_split_by_field_name()
            )
        )

        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee.id,
            ])],
            'split_by_field_name': 'tag_ids',
            'utilization_format': 'percentage',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_12(self):
        project = self.SudoProject.create({
            'name': 'Project #12',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #12',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #12',
            'employee_id': employee.id,
            'date': self.saturday,
            'unit_amount': 1,
        })
        wizard = self.Wizard.create({
            'date_from': self.saturday,
            'date_to': self.saturday,
            'employee_ids': [(6, False, [
                employee.id,
            ])],
            'utilization_format': 'percentage',
        })
        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)

    def test_entry_with_no_task(self):
        """Test empty data (task is empty)"""
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #13',
        })
        self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #13',
            'employee_id': employee.id,
            'date': self.wednesday,
            'unit_amount': 1,
        })

        wizard = self.Wizard.create({
            'date_from': self.wednesday,
            'date_to': self.wednesday,
            'employee_ids': [(6, False, [
                employee.id,
            ])],
            'entry_field_ids': [(0, False, {
                'sequence': 10,
                'field_name': 'employee_id',
            }), (0, False, {
                'sequence': 11,
                'field_name': 'project_id',
            }), (0, False, {
                'sequence': 12,
                'field_name': 'task_id',
            })],
        })

        wizard.action_export_xlsx()

        report = self.Report.create(
            wizard._collect_report_values()
        )
        self.IrActionReport._get_report_from_name(
            'hr_utilization_report.report'
        ).render_xlsx(report.ids, None)
