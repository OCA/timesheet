# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo.tests import common


class TestHrUtilizationAnalysis(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.Project = self.env["project.project"]
        self.HrEmployee = self.env["hr.employee"]
        self.AccountAnalyticLine = self.env["account.analytic.line"]
        self.Wizard = self.env["hr.utilization.analysis.wizard"]
        self.Analysis = self.env["hr.utilization.analysis"]

    def test_computation(self):
        project = self.Project.create({"name": "Project"})
        employee_1 = self.HrEmployee.create({"name": "Employee 1"})
        employee_2 = self.HrEmployee.create({"name": "Employee  2", "active": False})
        employee_3 = self.HrEmployee.create({"name": "Employee  3"})
        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry 1",
                "employee_id": employee_1.id,
                "date": date(2020, 6, 5),
                "unit_amount": 4,
            }
        )
        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "name": "Time Entry 2",
                "employee_id": employee_1.id,
                "date": date(2020, 6, 8),
                "unit_amount": 4,
            }
        )

        wizard = self.Wizard.create(
            {
                "date_from": date(2020, 6, 1),
                "date_to": date(2020, 6, 14),
                "employee_ids": [
                    (6, False, [employee_1.id, employee_2.id, employee_3.id])
                ],
            }
        )
        wizard.action_view()

        analysis = self.Analysis.create(wizard._collect_analysis_values())
        self.assertEqual(len(analysis.entry_ids), 28)

        employee_1_entries = analysis.entry_ids.filtered(
            lambda entry: entry.employee_id == employee_1
        )
        self.assertEqual(sum(employee_1_entries.mapped("capacity")), 80)
        self.assertEqual(sum(employee_1_entries.mapped("amount")), 8)
        self.assertEqual(sum(employee_1_entries.mapped("difference")), 72)

        entry_1 = employee_1_entries.filtered(
            lambda entry: entry.date == date(2020, 6, 5)
        )
        self.assertEqual(entry_1.difference, 4)

        entry_2 = employee_1_entries.filtered(
            lambda entry: entry.date == date(2020, 6, 8)
        )
        self.assertEqual(entry_2.difference, 4)
