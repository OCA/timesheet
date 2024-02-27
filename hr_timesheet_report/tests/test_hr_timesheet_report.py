# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2024 Tecnativa - Victor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestHrTimesheetReportBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.IrActionReport = cls.env["ir.actions.report"]
        cls.Wizard = cls.env["hr.timesheet.report.wizard"]
        cls.project = cls.env["project.project"].create({"name": "Project"})
        cls.employee = cls.env["hr.employee"].create({"name": "Employee"})
        cls.timesheet_1 = cls.env["account.analytic.line"].create(
            {
                "project_id": cls.project.id,
                "name": "Time Entry",
                "employee_id": cls.employee.id,
                "date": cls.today,
                "unit_amount": 1,
            }
        )

    def _create_report_from_wizard(self, wizard):
        return self.env["hr.timesheet.report"].create(wizard._collect_report_values())


class TestHrTimesheetReport(TestHrTimesheetReportBase):
    @mute_logger("odoo.models.unlink")
    def test_html_export(self):
        wizard_form = Form(self.Wizard)
        wizard_form.employee_ids.add(self.employee)
        wizard = wizard_form.save()
        self.assertTrue(wizard.grouping_field_ids)
        self.assertTrue(wizard.entry_field_ids)
        wizard.action_export_html()
        report = self._create_report_from_wizard(wizard)
        self.IrActionReport._render_qweb_html("hr_timesheet_report.report", report.ids)

    @mute_logger("odoo.models.unlink")
    def test_pdf_export(self):
        wizard_form = Form(self.Wizard)
        wizard_form.employee_ids.add(self.employee)
        wizard = wizard_form.save()
        self.assertTrue(wizard.grouping_field_ids)
        self.assertTrue(wizard.entry_field_ids)
        wizard.action_export_pdf()
        report = self._create_report_from_wizard(wizard)
        self.IrActionReport._render_qweb_html("hr_timesheet_report.report", report.ids)

    @mute_logger("odoo.models.unlink")
    def test_xlsx_export(self):
        wizard_form = Form(self.Wizard)
        wizard_form.employee_ids.add(self.employee)
        wizard = wizard_form.save()
        self.assertTrue(wizard.grouping_field_ids)
        self.assertTrue(wizard.entry_field_ids)
        report = self._create_report_from_wizard(wizard)
        self.IrActionReport._render_xlsx("hr_timesheet_report.report", report.ids, None)

    @mute_logger("odoo.models.unlink")
    def test_no_grouping(self):
        wizard_form = Form(
            self.Wizard.with_context(default_grouping_field_ids=[(5, False, False)])
        )
        wizard_form.date_from = self.today
        wizard_form.date_to = self.today
        wizard_form.employee_ids.add(self.employee)
        wizard = wizard_form.save()
        self.assertFalse(wizard.grouping_field_ids)
        self.assertTrue(wizard.entry_field_ids)
        report = self._create_report_from_wizard(wizard)
        self.assertEqual(len(report.group_ids), 1)
        self.assertEqual(report.total_unit_amount, 1)


class TestHrTimesheetReportMultiProject(TestHrTimesheetReportBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.extra_project = cls.env["project.project"].create({"name": "Extra Project"})
        cls.timesheet_2 = cls.env["account.analytic.line"].create(
            {
                "project_id": cls.extra_project.id,
                "name": "Time Entry 2",
                "employee_id": cls.employee.id,
                "date": cls.today,
                "unit_amount": 2,
            }
        )

    @mute_logger("odoo.models.unlink")
    def test_multi_project_01(self):
        entries = self.timesheet_1 + self.timesheet_2
        res = entries.action_timesheet_report_wizard()
        wizard_form = Form(self.env[res["res_model"]].with_context(**res["context"]))
        wizard = wizard_form.save()
        self.assertTrue(wizard.grouping_field_ids)
        self.assertTrue(wizard.entry_field_ids)
        report = self._create_report_from_wizard(wizard)
        self.assertEqual(len(report.group_ids), 2)
        self.assertEqual(len(report.line_ids), 2)
        self.assertIn(self.timesheet_1, report.line_ids)
        self.assertIn(self.timesheet_2, report.line_ids)
        self.assertEqual(report.total_unit_amount, 3)

    @mute_logger("odoo.models.unlink")
    def test_multi_project_02(self):
        wizard_form = Form(self.Wizard)
        wizard_form.date_from = self.today
        wizard_form.date_to = self.today
        wizard_form.employee_ids.add(self.employee)
        wizard = wizard_form.save()
        self.assertTrue(wizard.grouping_field_ids)
        self.assertTrue(wizard.entry_field_ids)
        report = self._create_report_from_wizard(wizard)
        self.assertEqual(len(report.group_ids), 2)
        self.assertEqual(report.total_unit_amount, 3)
