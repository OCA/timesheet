# Copyright 2024 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestHrTimesheetSheetWarning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sheet_warning_definition_model = cls.env[
            "hr_timesheet.sheet.warning.definition"
        ]
        cls.sheet_model = cls.env["hr_timesheet.sheet"]
        cls.project_model = cls.env["project.project"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.employee_model = cls.env["hr.employee"]

        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.env.user.company_ids += cls.company

        cls.user = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id)],
                }
            )
        )
        cls.employee = cls.employee_model.create(
            {
                "name": "Test Employee",
                "user_id": cls.user.id,
                "company_id": cls.user.company_id.id,
            }
        )

        cls.project = cls.project_model.create(
            {
                "name": "Project 1",
                "company_id": cls.user.company_id.id,
                "allow_timesheets": True,
                "user_id": cls.user.id,
            }
        )
        cls.timesheet = cls.aal_model.create(
            {
                "name": "Test Timesheet",
                "project_id": cls.project.id,
                "employee_id": cls.employee.id,
                "unit_amount": 5,
            }
        )

    def test_01_timesheet_warnings(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet_form.date_start = "2024-02-18"
        sheet_form.date_end = "2024-02-18"
        sheet = sheet_form.save()
        warning_definition = self.sheet_warning_definition_model.create(
            {
                "name": "Test Warning Definition",
                "python_code": "sheet.date_start == sheet.date_end",
            }
        )

        sheet.action_generate_warnings()
        self.assertEqual(len(sheet.hr_timesheet_sheet_warning_item_ids), 1)
        warning_item = sheet.hr_timesheet_sheet_warning_item_ids[0]
        self.assertEqual(warning_item.warning_definition_id.id, warning_definition.id)
        self.assertEqual(warning_item.sheet_id.id, sheet.id)

        warning_definition.write({"python_code": "sheet.date_start != sheet.date_end"})
        sheet.action_generate_warnings()
        self.assertEqual(len(sheet.hr_timesheet_sheet_warning_item_ids), 0)

    def test_02_timesheet_warnings(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet = sheet_form.save()
        warning_definition = self.sheet_warning_definition_model.create(
            {
                "name": "Test Warning Definition",
                "python_code": "sheet.total_time > 40",
            }
        )
        sheet.action_generate_warnings()
        self.assertEqual(len(sheet.hr_timesheet_sheet_warning_item_ids), 0)

        sheet.write({"total_time": 45})
        sheet.action_generate_warnings()
        self.assertEqual(len(sheet.hr_timesheet_sheet_warning_item_ids), 1)
        warning_item = sheet.hr_timesheet_sheet_warning_item_ids[0]
        self.assertEqual(warning_item.warning_definition_id.id, warning_definition.id)
        self.assertEqual(warning_item.sheet_id.id, sheet.id)

        warning_definition.write({"active": False})
        sheet.action_generate_warnings()
        self.assertEqual(len(sheet.hr_timesheet_sheet_warning_item_ids), 0)
        warning_definition.write({"active": True})
        sheet.action_generate_warnings()
        self.assertEqual(len(sheet.hr_timesheet_sheet_warning_item_ids), 1)

    def test_03_timesheet_warnings_with_domain(self):
        sheet_form_1 = Form(self.sheet_model.with_user(self.user))
        sheet_form_1.date_start = "2024-02-05"
        sheet_form_1.date_end = "2024-02-11"
        sheet_1 = sheet_form_1.save()

        sheet_form_2 = Form(self.sheet_model.with_user(self.user))
        sheet_form_2.date_start = "2024-02-12"
        sheet_form_2.date_end = "2024-02-18"
        sheet_2 = sheet_form_2.save()

        warning_definition = self.sheet_warning_definition_model.create(
            {
                "name": "Test Warning Definition",
                "python_code": "sheet.total_time < 10",
            }
        )

        sheet_1.action_generate_warnings()
        sheet_2.action_generate_warnings()
        self.assertEqual(len(sheet_1.hr_timesheet_sheet_warning_item_ids), 1)
        self.assertEqual(len(sheet_2.hr_timesheet_sheet_warning_item_ids), 1)

        warning_definition.write(
            {"warning_domain": "[('date_start', '=', '2024-02-05')]"}
        )
        sheet_1.action_generate_warnings()
        sheet_2.action_generate_warnings()
        self.assertEqual(len(sheet_1.hr_timesheet_sheet_warning_item_ids), 1)
        self.assertEqual(len(sheet_2.hr_timesheet_sheet_warning_item_ids), 0)
        sheet_2.action_generate_warnings()
        self.assertEqual(len(sheet_2.hr_timesheet_sheet_warning_item_ids), 0)

    def test_04_timesheet_warnings_on_confirm(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet = sheet_form.save()
        with patch.object(type(sheet), "action_generate_warnings") as patched:
            sheet.action_timesheet_confirm()
            patched.assert_called_once_with()

    def test_05_timesheet_warning_items(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet = sheet_form.save()
        warning_definition = self.sheet_warning_definition_model.create(
            {
                "name": "Test Warning Definition",
                "python_code": "sheet.total_time > 40",
            }
        )
        sheet.write({"total_time": 45})
        sheet.action_generate_warnings()
        warning_item = sheet.hr_timesheet_sheet_warning_item_ids

        default_display_name = (
            warning_definition.display_name + " in " + sheet.complete_name
        )
        self.assertEqual(warning_item.name, default_display_name)
        warning_item.write({"name": "Test Name"})
        self.assertEqual(warning_item.name, "Test Name")
        warning_item._compute_name()
        self.assertEqual(warning_item.name, default_display_name)

    def test_06_timesheet_warning_definitions(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet = sheet_form.save()
        warning_definition = self.sheet_warning_definition_model.create(
            {
                "name": "Test Warning Definition",
                "python_code": "123ABC",
            }
        )

        with self.assertRaises(UserError):
            warning_definition.evaluate_definition(sheet)
        warning_definition.write({"python_code": "True"})
        warning_definition.evaluate_definition(sheet)
