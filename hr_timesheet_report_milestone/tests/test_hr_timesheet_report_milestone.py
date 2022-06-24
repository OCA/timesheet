from odoo import fields
from odoo.tests import common


class TestHrTimesheetReport(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.today = fields.Date.today()
        self.Project = self.env["project.project"]
        self.HrEmployee = self.env["hr.employee"]
        self.Wizard = self.env["hr.timesheet.report.wizard"]
        self.Report = self.env["hr.timesheet.report"]
        self.Account = self.env["account.analytic.account"]
        self.account1 = self.Account.create(
            {
                "name": "Test Account 1",
            }
        )
        self.project1 = self.Project.create(
            {
                "name": "Test Project 1",
                "analytic_account_id": self.account1.id,
            }
        )
        self.employee = self.HrEmployee.create(
            {
                "name": "Employee",
            }
        )
        self.analytic_line = self.env["account.analytic.line"].create(
            {
                "project_id": self.project1.id,
                "account_id": self.account1.id,
                "name": "Test line",
            }
        )

    def test_domain_1(self):
        wizard = self.Wizard.create(
            {
                "date_from": self.today,
                "date_to": self.today,
                "employee_ids": [(6, False, [self.employee.id])],
                "grouping_field_ids": self.Wizard._default_grouping_field_ids(),
                "entry_field_ids": self.Wizard._default_entry_field_ids(),
                "line_ids": [(6, 0, self.analytic_line.ids)],
                "analytic_line_domain": [("id", "!=", self.analytic_line.id)],
            }
        )
        vals = wizard._collect_report_values()
        report = self.Report.create(vals)
        self.assertEqual(len(report.group_ids), 0)

    def test_domain_2(self):
        wizard = self.Wizard.create(
            {
                "date_from": self.today,
                "date_to": self.today,
                "employee_ids": [(6, False, [self.employee.id])],
                "grouping_field_ids": self.Wizard._default_grouping_field_ids(),
                "entry_field_ids": self.Wizard._default_entry_field_ids(),
                "line_ids": [(6, 0, self.analytic_line.ids)],
            }
        )
        vals = wizard._collect_report_values()
        report = self.Report.create(vals)
        self.assertEqual(len(report.group_ids), 1)
