# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2024 Tecnativa - Victor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import MagicMock, patch

from psycopg2 import IntegrityError

from odoo import Command, fields
from odoo.exceptions import UserError
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
            self.Wizard.with_context(default_grouping_field_ids=[Command.clear()])
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


class TestAccountAnalyticLineTimesheetWizardAction(TestHrTimesheetReportMultiProject):
    @mute_logger("odoo.models.unlink")
    def test_action_timesheet_report_wizard_action_dict(self):
        # Single entry
        res = self.timesheet_1.action_timesheet_report_wizard()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "hr.timesheet.report.wizard")
        self.assertEqual(res["views"], [[False, "form"]])
        self.assertEqual(res["target"], "new")
        self.assertEqual(
            res["context"].get("default_line_ids"),
            [Command.set([self.timesheet_1.id])],
        )
        wizard_form = Form(self.env[res["res_model"]].with_context(**res["context"]))
        wizard = wizard_form.save()
        self.assertEqual(wizard.line_ids, self.timesheet_1)

        # Multiple entries
        entries = self.timesheet_1 + self.timesheet_2
        res = entries.action_timesheet_report_wizard()
        self.assertEqual(res["type"], "ir.actions.act_window")
        self.assertEqual(res["res_model"], "hr.timesheet.report.wizard")
        self.assertEqual(res["views"], [[False, "form"]])
        self.assertEqual(res["target"], "new")
        default_line_ids = res["context"].get("default_line_ids")
        self.assertTrue(default_line_ids)
        self.assertEqual(default_line_ids[0][0], 6)
        self.assertEqual(default_line_ids[0][1], False)
        self.assertEqual(set(default_line_ids[0][2]), set(entries.ids))
        wizard_form = Form(self.env[res["res_model"]].with_context(**res["context"]))
        wizard = wizard_form.save()
        self.assertEqual(set(wizard.line_ids.ids), set(entries.ids))


class TestHrTimesheetReportExtraCoverage(TestHrTimesheetReportBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Report = cls.env["hr.timesheet.report"]
        cls.GroupByField = cls.env["hr.timesheet.report.field.groupby"]
        cls.EntryField = cls.env["hr.timesheet.report.field.entry"]
        cls.Group = cls.env["hr.timesheet.report.group"]
        cls.Entry = cls.env["hr.timesheet.report.entry"]
        cls.ReportXlsx = cls.env["report.hr_timesheet_report.report"]

    def _create_min_report(self, **vals):
        vals.setdefault("time_format", "decimal")
        return self.Report.create(vals)

    @mute_logger("odoo.models.unlink")
    def test_supported_report_types_and_time_format_selection(self):
        report = self._create_min_report()
        self.assertIn("qweb-html", report._supported_report_types())
        self.assertIn("xlsx", report._supported_report_types())
        selection = report._selection_time_format()
        self.assertIn(("decimal", "Decimal"), selection)

    @mute_logger("odoo.models.unlink")
    def test_get_domain_line_ids_priority(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        self.assertEqual(report._get_domain(), [("id", "in", [self.timesheet_1.id])])

    @mute_logger("odoo.models.unlink")
    def test_get_action_unsupported_type_raises(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        with self.assertRaises(UserError):
            report.get_action("nope")

    @mute_logger("odoo.models.unlink")
    def test_get_action_report_not_found_raises(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        IrActionsReportModel = type(self.env["ir.actions.report"])

        def _fake_search(self, domain, limit=None, **kwargs):
            # return empty recordset => triggers "not found"
            return self.browse()

        with patch.object(IrActionsReportModel, "search", _fake_search):
            with self.assertRaises(UserError):
                report.get_action("qweb-html")

    @mute_logger("odoo.models.unlink")
    def test_get_group_values_not_set_and_separator(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        self.GroupByField.create(
            {
                "report_id": report.id,
                "sequence": 10,
                "field_name": "project_id",
                "field_title": "Project",
                "field_type": "many2one",
            }
        )
        self.GroupByField.create(
            {
                "report_id": report.id,
                "sequence": 20,
                "field_name": "employee_id",
                "field_title": "Employee",
                "field_type": "many2one",
            }
        )
        vals = report._get_group_values(
            {
                "project_id": False,
                "employee_id": False,
                "__domain": [("id", "in", [self.timesheet_1.id])],
            }
        )
        self.assertIn("not set", vals["name"])
        self.assertIn("»", vals["name"])
        self.assertTrue(vals["scope"])

    @mute_logger("odoo.models.unlink")
    def test_field_groupby_compute_with_and_without_aggregation(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        f1 = self.EntryField.create(
            {
                "report_id": report.id,
                "sequence": 10,
                "field_name": "unit_amount",
                "field_title": "Qty",
                "field_type": "float",
                "aggregation": "sum",
            }
        )
        self.assertEqual(f1.groupby, "unit_amount:sum")
        f2 = self.EntryField.create(
            {
                "report_id": report.id,
                "sequence": 20,
                "field_name": "name",
                "field_title": "Name",
                "field_type": "char",
            }
        )
        self.assertEqual(f2.groupby, "name")

    @mute_logger("odoo.models.unlink")
    def test_field_name_unique_sql_constraint(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        self.EntryField.create(
            {
                "report_id": report.id,
                "sequence": 10,
                "field_name": "name",
                "field_title": "Name",
                "field_type": "char",
            }
        )
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(IntegrityError):
                self.EntryField.create(
                    {
                        "report_id": report.id,
                        "sequence": 20,
                        "field_name": "name",  # duplicate in same report
                        "field_title": "Name 2",
                        "field_type": "char",
                    }
                )

    @mute_logger("odoo.models.unlink")
    def test_entry_field_cell_classes(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        char_f = self.EntryField.create(
            {
                "report_id": report.id,
                "sequence": 10,
                "field_name": "name",
                "field_title": "Desc",
                "field_type": "char",
            }
        )
        self.assertEqual(char_f.cell_classes, "")
        non_char_f = self.EntryField.create(
            {
                "report_id": report.id,
                "sequence": 20,
                "field_name": "unit_amount",
                "field_title": "Qty",
                "field_type": "float",
            }
        )
        self.assertEqual(non_char_f.cell_classes, "text-nowrap")

    @mute_logger("odoo.models.unlink")
    def test_group_get_entry_values_domain_vs_id(self):
        report = self._create_min_report(line_ids=[Command.set([self.timesheet_1.id])])
        group = self.Group.create(
            {
                "report_id": report.id,
                "sequence": 10,
                "name": "G",
                "scope": str([("id", "in", [self.timesheet_1.id])]),
            }
        )
        vals = group._get_entry_values({"__domain": [("id", "=", self.timesheet_1.id)]})
        self.assertEqual(vals["scope"], str([("id", "=", self.timesheet_1.id)]))
        vals = group._get_entry_values({"id": self.timesheet_1.id})
        self.assertEqual(vals["scope"], [("id", "=", self.timesheet_1.id)])

    @mute_logger("odoo.models.unlink")
    def test_xlsx_amount_num_format_and_convert(self):
        report = self._create_min_report(time_format="decimal")
        self.assertEqual(self.ReportXlsx._get_amount_num_format(report), "0.00")
        self.assertEqual(self.ReportXlsx._convert_amount_num_format(report, 2.5), 2.5)
        report.time_format = "hh_mm"
        self.assertEqual(self.ReportXlsx._get_amount_num_format(report), "[h]:mm")
        self.assertEqual(self.ReportXlsx._convert_amount_num_format(report, 24.0), 1.0)
        report.time_format = "hh_mm_ss"
        self.assertEqual(self.ReportXlsx._get_amount_num_format(report), "[h]:mm:ss")
        self.assertEqual(self.ReportXlsx._convert_amount_num_format(report, 48.0), 2.0)


class TestHrTimesheetReportExtraBranches(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.Report = cls.env["hr.timesheet.report"]
        cls.GroupByField = cls.env["hr.timesheet.report.field.groupby"]
        cls.EntryField = cls.env["hr.timesheet.report.field.entry"]
        cls.ReportXlsx = cls.env["report.hr_timesheet_report.report"]
        cls.project = cls.env["project.project"].create({"name": "P"})
        cls.employee = cls.env["hr.employee"].create({"name": "E"})
        cls.department = cls.env["hr.department"].create({"name": "D"})
        cls.employee.department_id = cls.department
        cls.task = cls.env["project.task"].create(
            {"name": "T", "project_id": cls.project.id}
        )
        cls.employee_tag = cls.env["hr.employee.category"].create({"name": "Tag"})
        cls.employee.category_ids = [Command.link(cls.employee_tag.id)]
        cls.timesheet = cls.env["account.analytic.line"].create(
            {
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "name": "Time Entry",
                "employee_id": cls.employee.id,
                "date": cls.today,
                "unit_amount": 1,
            }
        )

    def _entry_field_cmd(self):
        return [
            Command.create(
                {
                    "sequence": 10,
                    "field_name": "name",
                    "field_title": "Name",
                    "field_type": "char",
                },
            )
        ]

    @mute_logger("odoo.models.unlink")
    def test_compute_group_ids_skips_empty_group_values(self):
        report = self.Report.create(
            {
                "time_format": "decimal",
                "line_ids": [Command.set([self.timesheet.id])],
                "entry_field_ids": self._entry_field_cmd(),
                "groupby_field_ids": [
                    Command.create(
                        {
                            "sequence": 10,
                            "field_name": "project_id",
                            "field_title": "Project",
                            "field_type": "many2one",
                        },
                    )
                ],
            }
        )
        ReportModel = type(self.env["hr.timesheet.report"])
        with patch.object(ReportModel, "_get_group_values", return_value={}):
            report._compute_group_ids()
        self.assertFalse(report.group_ids)

    @mute_logger("odoo.models.unlink")
    def test_get_domain_includes_project_task_employee_department(self):
        report = self.Report.create(
            {
                "time_format": "decimal",
                "date_from": self.today,
                "date_to": self.today,
                "project_ids": [Command.set([self.project.id])],
                "task_ids": [Command.set([self.task.id])],
                "employee_category_ids": [Command.set([self.employee_tag.id])],
                "department_ids": [Command.set([self.department.id])],
                "entry_field_ids": self._entry_field_cmd(),
            }
        )
        domain = report._get_domain()
        self.assertIn(("project_id", "in", [self.project.id]), domain)
        self.assertIn(("task_id", "in", [self.task.id]), domain)
        self.assertIn(("employee_id", "in", [self.employee.id]), domain)
        self.assertIn(("department_id", "in", [self.department.id]), domain)

    @mute_logger("odoo.models.unlink")
    def test_generate_xlsx_report_total_without_sections(self):
        report = self.Report.create(
            {
                "time_format": "decimal",
                "line_ids": [Command.set([self.timesheet.id])],
                "groupby_field_ids": [
                    Command.clear()
                ],  # no grouping => group.name == None
                # len == 1 => amount_column_index == 1
                "entry_field_ids": self._entry_field_cmd(),
            }
        )
        _ = report.group_ids
        for g in report.group_ids:
            _ = g.entry_ids
        workbook = MagicMock()
        sheet = MagicMock()
        workbook.add_worksheet.return_value = sheet
        workbook.add_format.return_value = object()
        self.ReportXlsx.generate_xlsx_report(workbook, None, report)

        # 1) "Total" written via sheet.write (because amount_column_index == 1)
        total_calls = [
            c
            for c in sheet.write.call_args_list
            if len(c.args) >= 3 and c.args[2] == "Total"
        ]
        self.assertTrue(total_calls)

        # 2) else branch formula with ":" range
        formula_calls = [
            c for c in sheet.write_formula.call_args_list if ":" in str(c.args[2])
        ]
        self.assertTrue(formula_calls)
