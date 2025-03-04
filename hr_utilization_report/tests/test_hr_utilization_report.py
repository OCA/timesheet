# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHrUtilizationReport(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wednesday = date(2018, 2, 6)
        cls.saturday = date(2018, 2, 2)
        cls.IrActionReport = cls.env["ir.actions.report"]
        cls.Project = cls.env["project.project"]
        cls.SudoProject = cls.Project.sudo()
        cls.HrEmployee = cls.env["hr.employee"]
        cls.SudoHrEmployee = cls.HrEmployee.sudo()
        cls.AccountAnalyticLine = cls.env["account.analytic.line"]
        cls.SudoAccountAnalyticLine = cls.AccountAnalyticLine.sudo()
        cls.Wizard = cls.env["hr.utilization.report.wizard"]
        cls.Report = cls.env["hr.utilization.report"]

    def test_1(self):
        project = self.SudoProject.create(
            {
                "name": "Project #1",
            }
        )
        employee_1 = self.SudoHrEmployee.create(
            {
                "name": "Employee #1-1",
            }
        )
        employee_2 = self.SudoHrEmployee.create(
            {
                "name": "Employee #1-2",
                "active": False,
            }
        )
        employee_3 = self.SudoHrEmployee.create(
            {
                "name": "Employee #1-3",
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #1-1",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 4,
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #1-2",
                "employee_id": employee_1.id,
                "date": self.wednesday - relativedelta(days=1),
                "unit_amount": 4,
            }
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [
                    Command.set(
                        [
                            employee_1.id,
                            employee_2.id,
                            employee_3.id,
                        ],
                    )
                ],
            }
        )

        report = self.Report.create(wizard._collect_report_values())
        self.assertEqual(len(report.group_ids), 1)
        self.assertEqual(len(report.group_ids[0].block_ids), 2)
        self.assertEqual(report.total_unit_amount_a, 4.0)
        self.assertEqual(report.total_utilization_a, 0.25)
        self.assertEqual(report.total_unit_amount_b, 0.0)
        self.assertEqual(report.total_utilization_b, 0.0)

    def test_2(self):
        project = self.SudoProject.create(
            {
                "name": "Project #2",
            }
        )
        employee_1 = self.SudoHrEmployee.create(
            {
                "name": "Employee #2-1",
            }
        )
        employee_2 = self.SudoHrEmployee.create(
            {
                "name": "Employee #2-2",
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #2",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )
        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [
                    Command.set(
                        [
                            employee_1.id,
                            employee_2.id,
                        ],
                    )
                ],
            }
        )
        wizard.action_export_html()

        report = self.Report.create(wizard._collect_report_values())
        report_ref = "hr_utilization_report.report"
        self.IrActionReport._render_qweb_html(report_ref, report.ids, data={})

    def test_3(self):
        project = self.SudoProject.create(
            {
                "name": "Project #3",
            }
        )
        employee_1 = self.SudoHrEmployee.create(
            {
                "name": "Employee #3-1",
            }
        )
        employee_2 = self.SudoHrEmployee.create(
            {
                "name": "Employee #3-2",
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #3",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )
        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [
                    Command.set(
                        [
                            employee_1.id,
                            employee_2.id,
                        ],
                    )
                ],
            }
        )
        wizard.action_export_pdf()

        report = self.Report.create(wizard._collect_report_values())
        report_ref = "hr_utilization_report.report"
        self.IrActionReport._render_qweb_pdf(report_ref, report.ids, data={})

    def test_4(self):
        project = self.SudoProject.create({"name": "Project #4"})
        employee_1 = self.SudoHrEmployee.create({"name": "Employee #4-1"})
        employee_2 = self.SudoHrEmployee.create({"name": "Employee #4-2"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #4",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [Command.set([employee_1.id, employee_2.id])],
                "utilization_format": "percentage",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_5(self):
        project = self.SudoProject.create({"name": "Project #5"})
        employee_1 = self.SudoHrEmployee.create({"name": "Employee #5-1"})
        employee_2 = self.SudoHrEmployee.create({"name": "Employee #5-2"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #5",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [Command.set([employee_1.id, employee_2.id])],
                "utilization_format": "absolute",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_6(self):
        project = self.SudoProject.create({"name": "Project #6"})
        employee_1 = self.SudoHrEmployee.create({"name": "Employee #6-1"})
        employee_2 = self.SudoHrEmployee.create({"name": "Employee #6-2"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #6",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        selection_split_by_field_name = self.Wizard._selection_split_by_field_name()
        split_field = (
            selection_split_by_field_name[0][0]
            if selection_split_by_field_name
            else None
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [Command.set([employee_1.id, employee_2.id])],
                "split_by_field_name": split_field,
                "utilization_format": "percentage",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_7(self):
        project = self.SudoProject.create({"name": "Project #7"})
        employee_1 = self.SudoHrEmployee.create({"name": "Employee #7-1"})
        employee_2 = self.SudoHrEmployee.create({"name": "Employee #7-2"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #7",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        selection_split_by_field_name = self.Wizard._selection_split_by_field_name()
        split_field = (
            selection_split_by_field_name[0][0]
            if selection_split_by_field_name
            else None
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [Command.set([employee_1.id, employee_2.id])],
                "split_by_field_name": split_field,
                "utilization_format": "absolute",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_8(self):
        project = self.SudoProject.create(
            {
                "name": "Project #8",
            }
        )
        employee_1 = self.SudoHrEmployee.create(
            {
                "name": "Employee #8-1",
            }
        )
        employee_2 = self.SudoHrEmployee.create(
            {
                "name": "Employee #8-2",
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #8",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 4,
            }
        )

        with self.assertRaises(ValidationError):
            self.Wizard.create(
                {
                    "date_from": self.wednesday,
                    "date_to": self.wednesday,
                    "employee_ids": [
                        Command.set(
                            [
                                employee_1.id,
                                employee_2.id,
                            ],
                        )
                    ],
                    "grouping_field_ids": [
                        Command.create(
                            {
                                "sequence": 10,
                                "field_name": "department_id",
                            },
                        )
                    ],
                    "entry_field_ids": [
                        Command.create(
                            {
                                "sequence": 10,
                                "field_name": "project_id",
                            },
                        )
                    ],
                }
            )

    def test_9(self):
        project = self.SudoProject.create(
            {
                "name": "Project #9",
            }
        )
        employee_1 = self.SudoHrEmployee.create(
            {
                "name": "Employee #9-1",
            }
        )
        employee_2 = self.SudoHrEmployee.create(
            {
                "name": "Employee #9-2",
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #9",
                "employee_id": employee_1.id,
                "date": self.wednesday,
                "unit_amount": 4,
            }
        )

        self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [
                    Command.set(
                        [
                            employee_1.id,
                            employee_2.id,
                        ],
                    )
                ],
                "grouping_field_ids": [Command.set([])],
            }
        )

        with self.assertRaises(ValidationError):
            self.Wizard.create(
                {
                    "date_from": self.wednesday,
                    "date_to": self.wednesday,
                    "employee_ids": [
                        Command.set(
                            [
                                employee_1.id,
                                employee_2.id,
                            ],
                        )
                    ],
                    "entry_field_ids": [Command.set([])],
                }
            )

    def test_10(self):
        project = self.SudoProject.create({"name": "Project #10"})
        employee = self.SudoHrEmployee.create({"name": "Employee #10"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #10",
                "employee_id": employee.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        # Get valid fields for split_by_field_name
        valid_fields = [x[0] for x in self.Wizard._selection_split_by_field_name()]
        split_field = (
            valid_fields[0] if valid_fields else None
        )  # Pick the first valid option

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [Command.set([employee.id])],
                "split_by_field_name": split_field,
                "utilization_format": "percentage",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_11(self):
        project = self.SudoProject.create({"name": "Project #11"})
        employee = self.SudoHrEmployee.create({"name": "Employee #11"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #11",
                "employee_id": employee.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        # Get valid fields for split_by_field_name
        valid_fields = [x[0] for x in self.Wizard._selection_split_by_field_name()]
        split_field = (
            valid_fields[0] if valid_fields else None
        )  # Pick the first valid option

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [Command.set([employee.id])],
                "split_by_field_name": split_field,
                "utilization_format": "percentage",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_12(self):
        project = self.SudoProject.create({"name": "Project #12"})
        employee = self.SudoHrEmployee.create({"name": "Employee #12"})

        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #12",
                "employee_id": employee.id,
                "date": self.saturday,
                "unit_amount": 1,
            }
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.saturday,
                "date_to": self.saturday,
                "employee_ids": [Command.set([employee.id])],
                "utilization_format": "percentage",
            }
        )
        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )

    def test_entry_with_no_task(self):
        """Test empty data (task is empty)"""
        project = self.SudoProject.create(
            {
                "name": "Project #1",
            }
        )
        employee = self.SudoHrEmployee.create(
            {
                "name": "Employee #13",
            }
        )
        self.SudoAccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry #13",
                "employee_id": employee.id,
                "date": self.wednesday,
                "unit_amount": 1,
            }
        )

        wizard = self.Wizard.create(
            {
                "date_from": self.wednesday,
                "date_to": self.wednesday,
                "employee_ids": [
                    Command.set(
                        [
                            employee.id,
                        ],
                    )
                ],
                "entry_field_ids": [
                    Command.create(
                        {
                            "sequence": 10,
                            "field_name": "employee_id",
                        },
                    ),
                    Command.create(
                        {
                            "sequence": 11,
                            "field_name": "project_id",
                        },
                    ),
                    Command.create(
                        {
                            "sequence": 12,
                            "field_name": "task_id",
                        },
                    ),
                ],
            }
        )

        wizard.action_export_xlsx()

        report = self.Report.create(wizard._collect_report_values())
        self.IrActionReport._render_xlsx(
            "hr_utilization_report.report", report.ids, {"report": report}
        )
