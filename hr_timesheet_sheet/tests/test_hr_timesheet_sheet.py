# Copyright 2018-2020 ForgeFlow, S.L.
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import Form, SavepointCase

from ..models.hr_timesheet_sheet import empty_name


class TestHrTimesheetSheet(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        officer_group = cls.env.ref("hr.group_hr_user")
        multi_company_group = cls.env.ref("base.group_multi_company")
        sheet_user_group = cls.env.ref("hr_timesheet.group_hr_timesheet_user")
        project_user_group = cls.env.ref("project.group_project_user")
        cls.sheet_model = cls.env["hr_timesheet.sheet"].with_context(
            tracking_disable=True
        )
        cls.sheet_line_model = cls.env["hr_timesheet.sheet.line"]
        cls.project_model = cls.env["project.project"]
        cls.task_model = cls.env["project.task"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.aaa_model = cls.env["account.analytic.account"]
        cls.employee_model = cls.env["hr.employee"]
        cls.department_model = cls.env["hr.department"]
        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.company_2 = cls.env["res.company"].create(
            {"name": "Test company 2", "parent_id": cls.company.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.user.company_ids += cls.company_2

        cls.user = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User",
                    "login": "test_user",
                    "email": "test@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                officer_group.id,
                                sheet_user_group.id,
                                project_user_group.id,
                                multi_company_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id)],
                }
            )
        )

        cls.user_2 = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User 2",
                    "login": "test_user_2",
                    "email": "test2@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                officer_group.id,
                                sheet_user_group.id,
                                project_user_group.id,
                                multi_company_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company_2.id,
                    "company_ids": [(4, cls.company_2.id)],
                }
            )
        )

        cls.user_3 = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User 3",
                    "login": "test_user_3",
                    "email": "test3@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                sheet_user_group.id,
                                project_user_group.id,
                                multi_company_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id)],
                }
            )
        )

        cls.user_4 = (
            cls.env["res.users"]
            .with_user(cls.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User 4",
                    "login": "test_user_4",
                    "email": "test4@oca.com",
                    "groups_id": [
                        (
                            6,
                            0,
                            [
                                officer_group.id,
                                sheet_user_group.id,
                                project_user_group.id,
                                multi_company_group.id,
                            ],
                        )
                    ],
                    "company_id": cls.company.id,
                    "company_ids": [(4, cls.company.id)],
                }
            )
        )

        cls.employee_manager = cls.employee_model.create(
            {
                "name": "Test Manager",
                "user_id": cls.user_2.id,
                "company_id": cls.user.company_id.id,
            }
        )

        cls.employee = cls.employee_model.create(
            {
                "name": "Test Employee",
                "user_id": cls.user.id,
                "parent_id": cls.employee_manager.id,
                "company_id": cls.user.company_id.id,
            }
        )

        cls.employee_no_user = cls.employee_model.create(
            {
                "name": "Test Employee (no user)",
                "parent_id": cls.employee_manager.id,
                "company_id": cls.user.company_id.id,
            }
        )

        cls.department_manager = cls.employee_model.create(
            {
                "name": "Test Department Manager",
                "user_id": cls.user_3.id,
                "company_id": cls.user.company_id.id,
            }
        )

        cls.employee_4 = cls.employee_model.create(
            {
                "name": "Test User 4",
                "user_id": cls.user_4.id,
                "parent_id": cls.department_manager.id,
                "company_id": cls.user.company_id.id,
            }
        )

        cls.department = cls.department_model.create(
            {"name": "Department test", "company_id": cls.user.company_id.id}
        )

        cls.employee.department_id = cls.department

        cls.department_2 = cls.department_model.create(
            {
                "name": "Department test 2",
                "company_id": cls.user.company_id.id,
                "manager_id": cls.department_manager.id,
            }
        )

        cls.project_1 = cls.project_model.create(
            {
                "name": "Project 1",
                "company_id": cls.user.company_id.id,
                "allow_timesheets": True,
                "user_id": cls.user_3.id,
            }
        )
        cls.project_2 = cls.project_model.create(
            {
                "name": "Project 2",
                "company_id": cls.user.company_id.id,
                "allow_timesheets": True,
                "user_id": cls.user_4.id,
            }
        )
        cls.task_1 = cls.task_model.create(
            {
                "name": "Task 1",
                "project_id": cls.project_1.id,
                "company_id": cls.user.company_id.id,
            }
        )
        cls.task_2 = cls.task_model.create(
            {
                "name": "Task 2",
                "project_id": cls.project_2.id,
                "company_id": cls.user.company_id.id,
            }
        )

    def test_0(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        self.assertEqual(len(sheet_form.line_ids), 0)

        sheet = sheet_form.save()
        self.assertEqual(sheet.company_id, self.user.company_id)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertTrue(sheet.employee_id)

        with Form(sheet.with_user(self.user)) as sheet_form:
            sheet_form.add_line_project_id = self.project_1
        sheet.button_add_line()
        # hack: because we cannot call button_add_line in edit mode in the test
        sheet.with_context(sheet_write=True)._compute_line_ids()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

        # this part of code doesn't make sense because sheet is in draft:

        # sheet.date_end = sheet.date_end + relativedelta(days=1)
        # sheet._onchange_timesheets()
        # self.assertEqual(len(sheet.timesheet_ids), 0)
        # self.assertEqual(len(sheet.line_ids), 0)

    def test_1(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        self.assertEqual(sheet_form.employee_id.id, self.employee.id)
        self.assertEqual(sheet_form.department_id.id, self.department.id)
        self.assertEqual(len(sheet_form.timesheet_ids), 0)
        self.assertEqual(len(sheet_form.line_ids), 0)

        with sheet_form.timesheet_ids.new() as timesheet:
            timesheet.name = "test"
            timesheet.project_id = self.project_1
        self.assertEqual(sheet_form.employee_id.id, self.employee.id)
        self.assertEqual(len(sheet_form.timesheet_ids), 1)
        self.assertEqual(len(sheet_form.line_ids), 7)
        self.assertFalse(
            any([line.get("unit_amount") for line in sheet_form.line_ids._records])
        )
        timesheet = sheet_form.timesheet_ids._records[0]
        self.assertEqual(timesheet.get("unit_amount"), 0)

        with sheet_form.timesheet_ids.edit(0) as timesheet:
            timesheet.unit_amount = 1.0
        self.assertEqual(len(sheet_form.timesheet_ids), 1)
        self.assertEqual(len(sheet_form.line_ids), 7)
        self.assertTrue(
            any([line.get("unit_amount") for line in sheet_form.line_ids._records])
        )

        sheet = sheet_form.save()
        sheet_form = Form(
            sheet.with_user(self.user).with_context(
                params={"model": "hr_timesheet.sheet", "id": sheet.id}
            )
        )

        lines_to_edit = [
            i
            for i, x in enumerate(sheet_form.line_ids._records)
            if x.get("unit_amount")
        ]
        with sheet_form.line_ids.edit(lines_to_edit[0]) as line:
            line.unit_amount = 2.0

        line = sheet_form.line_ids._records[lines_to_edit[0]]
        self.assertEqual(line.get("unit_amount"), 2.0)
        timesheet = sheet_form.timesheet_ids._records[0]
        self.assertEqual(timesheet.get("unit_amount"), 1.0)

        sheet = sheet_form.save()
        self.assertEqual(len(sheet.timesheet_ids), 2)
        self.assertEqual(len(sheet.line_ids), 7)

    def test_1_B(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        with sheet_form.timesheet_ids.new() as timesheet:
            timesheet.name = "test"
            timesheet.date = self.sheet_model._default_date_start()
            timesheet.project_id = self.project_1
            timesheet.unit_amount = 1.0
        self.assertEqual(sheet_form.employee_id.id, self.employee.id)
        self.assertEqual(len(sheet_form.timesheet_ids), 1)
        self.assertEqual(len(sheet_form.line_ids), 7)
        self.assertEqual(sheet_form.state, "new")

        sheet = sheet_form.save()
        self.assertEqual(sheet.state, "draft")
        sheet_form = Form(
            sheet.with_user(self.user).with_context(
                params={"model": "hr_timesheet.sheet", "id": sheet.id}
            )
        )

        with sheet_form.line_ids.new() as line:
            line.date = self.sheet_model._default_date_start()
            line.project_id = self.project_1
            line.employee_id = self.employee
            line.unit_amount = 1.0
        self.assertEqual(len(sheet_form.timesheet_ids), 1)
        self.assertEqual(len(sheet_form.line_ids), 8)

        sheet = sheet_form.save()
        self.assertEqual(len(sheet.line_ids), 7)

    def test_2(self):
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        self.assertEqual(sheet.department_id.id, self.department.id)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertEqual(len(sheet.line_ids), 0)

        self.employee._compute_timesheet_sheet_count()
        self.assertEqual(self.employee.timesheet_sheet_count, 1)
        self.department._compute_timesheet_to_approve()
        self.assertEqual(self.department.timesheet_sheet_to_approve_count, 0)

        with Form(sheet.with_user(self.user)) as sheet_form:
            sheet_form.add_line_project_id = self.project_1
        sheet.button_add_line()
        # hack: because we cannot call button_add_line in edit mode in the test
        sheet.with_context(sheet_write=True)._compute_line_ids()
        self.assertFalse(sheet.add_line_project_id.id)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)

        with Form(sheet.with_user(self.user)) as sheet_form:
            with sheet_form.line_ids.edit(0) as line_form:
                line_form.unit_amount = 2.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        line = fields.first(sheet.line_ids)
        self.assertEqual(line.unit_amount, 2.0)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        timesheet = fields.first(sheet.timesheet_ids)

        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("date") != fields.Date.to_string(timesheet.date)
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                self.assertEqual(line_form.unit_amount, 0.0)
                line_form.unit_amount = 1.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        line2 = fields.first(
            sheet.line_ids.filtered(lambda l: l.date != timesheet.date)
        )
        self.assertEqual(line2.unit_amount, 1.0)
        self.assertEqual(len(sheet.timesheet_ids), 2)

        with Form(sheet.with_user(self.user)) as sheet_form:
            sheet_form.add_line_project_id = self.project_2
        sheet.button_add_line()
        # hack: because we cannot call button_add_line in edit mode in the test
        sheet.with_context(sheet_write=True)._compute_line_ids()
        self.assertEqual(len(sheet.timesheet_ids), 3)
        self.assertIn(timesheet.id, sheet.timesheet_ids.ids)
        self.assertEqual(len(sheet.line_ids), 14)

        self.assertEqual(sheet.state, "draft")
        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, "confirm")
        self.department._compute_timesheet_to_approve()
        self.assertEqual(self.department.timesheet_sheet_to_approve_count, 1)

        # Confirmed timesheet cannot be modified
        with self.assertRaises(UserError):
            timesheet.unit_amount = 0.0
        self.assertEqual(timesheet.unit_amount, 2.0)

        # Force confirmed timesheet to be modified
        timesheet.with_context(skip_check_state=True).unit_amount = 0.0
        self.assertEqual(timesheet.unit_amount, 0.0)

        with self.assertRaises(UserError):
            timesheet.unlink()
        sheet.action_timesheet_done()
        self.assertEqual(sheet.state, "done")
        with self.assertRaises(UserError):
            sheet.unlink()
        sheet.action_timesheet_draft()
        self.assertEqual(sheet.state, "draft")
        sheet.unlink()

    def test_3(self):
        timesheet = self.aal_model.create(
            {
                "name": empty_name,
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
            }
        )
        sheet_form = Form(self.sheet_model.with_user(self.user))
        self.assertEqual(len(sheet_form.line_ids), 7)
        self.assertEqual(len(sheet_form.timesheet_ids), 1)
        self.assertTrue(self.aal_model.search([("id", "=", timesheet.id)]))

        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        # analytic line cleaned up on form save
        self.assertFalse(self.aal_model.search([("id", "in", timesheets)]))
        self.assertEqual(len(sheet.line_ids), 0)
        self.assertEqual(len(sheet.timesheet_ids), 0)
        self.assertFalse(self.aal_model.search([("id", "=", timesheet.id)]))

    def test_4(self):
        timesheet_1 = self.aal_model.create(
            {
                "name": empty_name,
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
            }
        )
        timesheet_2 = self.aal_model.create(
            {
                "name": empty_name,
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 1.0,
            }
        )
        timesheet_3 = self.aal_model.create(
            {
                "name": "x",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
            }
        )
        # With this we assure to be in the same week but different day
        # (for covering today = sunday)
        days = -1 if timesheet_3.date.weekday() == 6 else 1
        timesheet_3.date = timesheet_3.date + relativedelta(days=days)

        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet = sheet_form.save()
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)

        timesheet_1_or_2 = self.aal_model.search(
            [("id", "in", [timesheet_1.id, timesheet_2.id])]
        )
        self.assertEqual(len(timesheet_1_or_2), 1)
        self.assertEqual(timesheet_1_or_2.unit_amount, 1.0)
        self.assertEqual(timesheet_3.unit_amount, 0.0)

        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 1.0)

        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = 0.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(line.unit_amount, 0.0)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertFalse(self.aal_model.search([("id", "=", timesheet_1_or_2.id)]))

        timesheet_3.name = empty_name
        with Form(sheet.with_user(self.user)) as sheet_form:
            sheet_form.add_line_project_id = self.project_2
            sheet_form.add_line_task_id = self.task_2
        sheet.button_add_line()
        # hack: because we cannot call button_add_line in edit mode in the test
        sheet.with_context(sheet_write=True)._compute_line_ids()
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertFalse(self.aal_model.search([("id", "=", timesheet_3.id)]))

    def test_5(self):
        timesheet_1 = self.aal_model.create(
            {
                "name": empty_name,
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        timesheet_2 = self.aal_model.create(
            {
                "name": "x",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        sheet_form = Form(self.sheet_model.with_user(self.user))
        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        sheet.timesheet_ids = [(6, 0, timesheets)]
        with Form(sheet.with_user(self.user)):
            pass  # trigger edit and save
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 2)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 4.0)

        timesheet_2.name = empty_name
        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = 3.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(fields.first(sheet.timesheet_ids).unit_amount, 3.0)

        timesheet_1_or_2 = self.aal_model.search(
            [("id", "in", [timesheet_1.id, timesheet_2.id])]
        )
        self.assertEqual(len(timesheet_1_or_2), 1)
        self.assertEqual(timesheet_1_or_2.unit_amount, 3.0)

        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = 4.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(fields.first(sheet.timesheet_ids).unit_amount, 4.0)
        self.assertEqual(timesheet_1_or_2.unit_amount, 4.0)

        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = -1.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 1)

    def test_6(self):
        timesheet_1 = self.aal_model.create(
            {
                "name": empty_name,
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        timesheet_2 = self.aal_model.create(
            {
                "name": "w",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        timesheet_3 = self.aal_model.create(
            {
                "name": "x",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        timesheet_4 = self.aal_model.create(
            {
                "name": "y",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        timesheet_5 = self.aal_model.create(
            {
                "name": "z",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        sheet_form = Form(self.sheet_model.with_user(self.user))
        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        sheet.timesheet_ids = [(6, 0, timesheets)]
        with Form(sheet.with_user(self.user)):
            pass  # trigger edit and save
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.timesheet_ids), 5)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 10.0)

        timesheet_2.name = empty_name
        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = 6.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(len(sheet.timesheet_ids), 3)

        timesheet_1_or_2 = self.aal_model.search(
            [("id", "in", [timesheet_1.id, timesheet_2.id])]
        )
        self.assertFalse(timesheet_1_or_2)

        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = 3.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(len(sheet.timesheet_ids), 4)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(line.unit_amount, 3.0)

        timesheet_3_4_and_5 = self.aal_model.search(
            [("id", "in", [timesheet_3.id, timesheet_4.id, timesheet_5.id])]
        )
        self.assertEqual(len(timesheet_3_4_and_5), 3)

        timesheet_6 = self.aal_model.create(
            {
                "name": "z",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
            }
        )
        timesheet_5.name = empty_name
        sheet_form = Form(sheet.with_user(self.user))
        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        sheet.timesheet_ids = [(6, 0, timesheets)]
        with Form(sheet.with_user(self.user)):
            pass  # trigger edit and save
        self.assertEqual(len(sheet.timesheet_ids), 4)
        line = sheet.line_ids.filtered(lambda l: l.unit_amount != 0.0)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 5.0)

        with Form(sheet.with_user(self.user)) as sheet_form:
            lines_to_edit = [
                i
                for i, x in enumerate(sheet_form.line_ids._records)
                if x.get("unit_amount") != 0.0
            ]
            with sheet_form.line_ids.edit(lines_to_edit[0]) as line_form:
                line_form.unit_amount = 1.0
                self.assertEqual(len(sheet.new_line_ids), 1)
        self.assertEqual(len(sheet.timesheet_ids), 4)
        self.assertTrue(timesheet_6.exists().ids)

    def test_end_date_before_start_date(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet_form.date_start = self.sheet_model._default_date_end()
        sheet_form.date_end = self.sheet_model._default_date_start()
        self.assertEqual(len(sheet_form.line_ids), 0)
        self.assertEqual(len(sheet_form.timesheet_ids), 0)
        sheet_form.save()
        # self assert something

    def test_no_copy(self):
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        with self.assertRaises(UserError):
            sheet.with_user(self.user).copy()

    def test_no_overlap(self):
        Form(self.sheet_model.with_user(self.user)).save()
        with self.assertRaises(ValidationError):
            Form(self.sheet_model.with_user(self.user)).save()

    def test_8(self):
        """Multicompany test"""
        employee_2 = self.employee_model.create(
            {
                "name": "Test User 2",
                "user_id": self.user_2.id,
                "company_id": self.user_2.company_id.id,
            }
        )
        department_2 = self.department_model.create(
            {"name": "Department test 2", "company_id": self.user_2.company_id.id}
        )
        project_3 = self.project_model.create(
            {"name": "Project 3", "company_id": self.user_2.company_id.id}
        )
        task_3 = self.task_model.create(
            {
                "name": "Task 3",
                "project_id": project_3.id,
                "company_id": self.user_2.company_id.id,
            }
        )
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        with self.assertRaises(ValidationError):
            with Form(sheet.with_user(self.user)) as sheet_form:
                with self.assertRaises(AssertionError):
                    sheet_form.company_id = self.user_2.company_id.id
                with self.assertRaises(AssertionError):
                    sheet_form.employee_id = employee_2
                with self.assertRaises(AssertionError):
                    sheet_form.department_id = department_2
                sheet_form.add_line_project_id = project_3
                sheet_form.add_line_task_id = task_3

    def test_9(self):
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        with Form(sheet.with_user(self.user)) as sheet_form:
            sheet_form.add_line_project_id = self.project_1
        sheet.button_add_line()
        # hack: because we cannot call button_add_line in edit mode in the test
        sheet.with_context(sheet_write=True)._compute_line_ids()
        self.assertEqual(len(sheet.timesheet_ids), 1)

        with self.assertRaises(UserError):
            sheet.action_timesheet_refuse()

        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, "confirm")

        sheet.action_timesheet_refuse()
        self.assertEqual(sheet.state, "draft")

        sheet.action_timesheet_confirm()
        self.assertEqual(sheet.state, "confirm")

        sheet.action_timesheet_done()
        self.assertEqual(sheet.state, "done")
        with self.assertRaises(UserError):
            sheet.unlink()

        sheet.action_timesheet_draft()
        self.assertEqual(sheet.state, "draft")
        sheet.unlink()

    def test_10_start_day(self):
        """Test that the start day can be configured for weekly timesheets."""
        self.company.timesheet_week_start = "6"
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        weekday_from = sheet.date_start.weekday()
        weekday_to = sheet.date_end.weekday()

        self.assertEqual(weekday_from, 6, "The timesheet should start on Sunday")
        self.assertEqual(weekday_to, 5, "The timesheet should end on Saturday")

    def test_11_onchange_unit_amount(self):
        """Test onchange unit_amount for line without sheet_id."""
        self.aal_model.create(
            {
                "name": "test1",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
                "date": self.sheet_model._default_date_start(),
            }
        )
        self.aal_model.create(
            {
                "name": "test2",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
                "date": self.sheet_model._default_date_start(),
            }
        )
        sheet_form = Form(self.sheet_model.with_user(self.user))
        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        sheet.timesheet_ids = [(6, 0, timesheets)]
        with Form(sheet.with_user(self.user)):
            pass  # trigger edit and save
        self.assertEqual(len(sheet.timesheet_ids), 2)
        self.assertEqual(len(sheet.line_ids), 7)

        unit_amount = 0.0
        for line in sheet.line_ids:
            if line.unit_amount:
                line.sheet_id = False
                unit_amount = line.unit_amount
                line.write({"unit_amount": unit_amount + 1.0})
                res_onchange = line.with_context(
                    params={"model": "hr_timesheet.sheet", "id": sheet.id}
                ).onchange_unit_amount()
                self.assertFalse(res_onchange)
                self.assertEqual(line.unit_amount, unit_amount + 1.0)
                line.sheet_id = sheet.id

        self.assertEqual(len(sheet.timesheet_ids), 2)
        self.assertEqual(len(sheet.line_ids), 7)
        self.assertEqual(len(sheet.new_line_ids), 1)

        new_line = fields.first(sheet.new_line_ids)
        self.assertEqual(new_line.unit_amount, unit_amount + 1.0)

        for line in sheet.line_ids:
            if line.unit_amount:
                line.sheet_id = False
                unit_amount = line.unit_amount
                line.write({"unit_amount": unit_amount + 1.0})
                res_onchange = line.onchange_unit_amount()
                warning = res_onchange.get("warning")
                self.assertTrue(warning)
                message = warning.get("message")
                self.assertTrue(message)
                line.sheet_id = sheet.id

    def test_12_creating_sheet(self):
        """Test onchange unit_amount for line without sheet_id."""
        self.aal_model.create(
            {
                "name": "test1",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "unit_amount": 2.0,
                "date": self.sheet_model._default_date_start(),
            }
        )
        sheet_form = Form(self.sheet_model.with_user(self.user))
        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        sheet.timesheet_ids = [(6, 0, timesheets)]
        with Form(sheet.with_user(self.user)):
            pass  # trigger edit and save
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

        line = sheet.line_ids.filtered(lambda l: l.unit_amount)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.unit_amount, 2.0)

        unit_amount = line.unit_amount
        with Form(line.with_user(self.user)) as line_form:
            line_form.unit_amount = unit_amount + 1.0
        self.assertEqual(line.unit_amount, 3.0)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(len(sheet.line_ids), 7)

    def test_13(self):
        sheet = Form(self.sheet_model.with_user(self.user)).save()

        self.assertIsNotNone(sheet.name)

        sheet.date_end = sheet.date_start + relativedelta(years=1)
        self.assertIsNotNone(sheet.name)

    def test_14_analytic_account_multicompany(self):
        new_employee = self.employee_model.create(
            {
                "name": "Test New Employee",
                "user_id": self.user_2.id,
                "company_id": self.company_2.id,
            }
        )
        sheet = Form(self.sheet_model.with_user(self.user_2)).save()
        self.assertEqual(sheet.company_id, self.company_2)

        timesheet_1 = self.aal_model.create(
            {
                "name": "test1",
                "project_id": self.project_1.id,
                "employee_id": new_employee.id,
                "unit_amount": 1.0,
                "date": self.sheet_model._default_date_start(),
            }
        )
        with self.assertRaises(ValidationError):
            timesheet_1.write({"sheet_id": sheet.id})

        new_project = self.project_model.create(
            {
                "name": "Project Test",
                "company_id": self.company_2.id,
                "allow_timesheets": True,
            }
        )
        timesheet_2 = self.aal_model.create(
            {
                "name": "test1",
                "project_id": new_project.id,
                "employee_id": new_employee.id,
                "unit_amount": 1.0,
                "date": self.sheet_model._default_date_start(),
            }
        )
        timesheet_2.write({"sheet_id": sheet.id})

    def test_15(self):
        """Test company constraint in Account Analytic Account."""
        self.aal_model.create(
            {
                "name": "test1",
                "project_id": self.project_1.id,
                "employee_id": self.employee.id,
                "company_id": self.company.id,
                "unit_amount": 2.0,
                "date": self.sheet_model._default_date_start(),
            }
        )
        self.assertNotEqual(self.company, self.company_2)
        sheet_form = Form(self.sheet_model.with_user(self.user))
        timesheets = [x.get("id") for x in sheet_form.timesheet_ids._records]
        sheet = sheet_form.save()
        sheet.timesheet_ids = [(6, 0, timesheets)]
        with Form(sheet.with_user(self.user)):
            pass  # trigger edit and save
        self.assertEqual(sheet.company_id, self.company)
        self.assertEqual(len(sheet.timesheet_ids), 1)
        self.assertEqual(sheet.timesheet_ids.company_id, self.company)

        analytic_account = sheet.timesheet_ids.account_id
        self.assertEqual(analytic_account.company_id, self.company)

        with self.assertRaises(AccessError):
            analytic_account.company_id = self.company_2

    def test_16(self):
        department = self.department_model.create(
            {"name": "Department test", "company_id": False}
        )
        self.user_16 = (
            self.env["res.users"]
            .with_user(self.env.user)
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Test User 16",
                    "login": "test_user_16",
                    "email": "test16@oca.com",
                    "company_id": self.company.id,
                    "company_ids": [(4, self.company.id)],
                }
            )
        )
        new_employee = self.employee_model.create(
            {
                "name": "Test User",
                "user_id": self.user_16.id,
                "company_id": self.company.id,
                "department_id": department.id,
            }
        )
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet_form.employee_id = new_employee
        sheet_form.department_id = self.department_model
        sheet_no_department = sheet_form.save()
        self.assertFalse(sheet_no_department.department_id)
        sheet_no_department._onchange_employee_id()
        self.assertTrue(sheet_no_department.department_id)
        self.assertEqual(sheet_no_department.department_id, department)
        self.assertTrue(sheet_no_department.company_id)

        sheet_no_department.unlink()
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet_form.employee_id = self.employee_model
        with self.assertRaises(AssertionError):
            sheet_form.save()

        sheet_with_employee = Form(self.sheet_model.with_user(self.user)).save()
        self.assertTrue(sheet_with_employee.employee_id)
        self.assertTrue(sheet_with_employee.department_id)
        self.assertTrue(sheet_with_employee.company_id)

    def test_sheet_range_monthly(self):
        self.company.sheet_range = "MONTHLY"
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        sheet._compute_name()
        self.assertEqual(sheet.date_start.day, 1)
        self.assertEqual(sheet.date_start.month, sheet.date_end.month)

    def test_sheet_range_daily(self):
        self.company.sheet_range = "DAILY"
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        sheet._compute_name()
        self.assertEqual(sheet.date_start, sheet.date_end)

    def test_employee_no_user(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        with self.assertRaises(UserError):
            sheet_form.employee_id = self.employee_no_user
            sheet_form.save()

        sheet = Form(self.sheet_model.with_user(self.user)).save()
        with Form(sheet.with_user(self.user)) as sheet_form:
            with self.assertRaises(AssertionError):
                sheet_form.employee_id = self.employee_no_user

    def test_workflow(self):
        sheet = Form(self.sheet_model.with_user(self.user)).save()

        self.sheet_model.with_user(self.user).fields_view_get(view_type="form")
        self.sheet_model.with_user(self.user).fields_view_get(view_type="tree")

        with self.assertRaises(UserError):
            sheet.with_user(self.user_3).action_timesheet_refuse()
        with self.assertRaises(UserError):
            sheet.with_user(self.user_3).action_timesheet_done()

        sheet.action_timesheet_confirm()
        self.assertFalse(sheet.with_user(self.user_3).can_review)
        self.assertEqual(
            self.sheet_model.with_user(self.user_3).search_count(
                [("can_review", "=", True)]
            ),
            0,
        )
        self.assertEqual(
            self.sheet_model.with_user(self.user_3).search_count(
                [("can_review", "!=", False)]
            ),
            0,
        )
        self.assertEqual(
            self.sheet_model.with_user(self.user_3).search_count(
                [("can_review", "=", False)]
            ),
            1,
        )
        self.assertEqual(
            self.sheet_model.with_user(self.user_3).search_count(
                [("can_review", "!=", True)]
            ),
            1,
        )
        with self.assertRaises(UserError):
            sheet.with_user(self.user_3).action_timesheet_draft()
        sheet.action_timesheet_done()
        sheet.action_timesheet_draft()
        sheet.unlink()

    def test_review_policy_default(self):
        self.assertEqual(self.company.timesheet_sheet_review_policy, "hr")
        sheet = Form(self.sheet_model.with_user(self.user)).save()
        self.assertEqual(sheet.review_policy, "hr")
        sheet.unlink()

    def test_same_week_different_years(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet_form.date_start = date(2019, 12, 30)
        sheet_form.date_end = date(2020, 1, 5)
        self.assertEqual(sheet_form.name, "Week 01, 2020")

    def test_different_weeks_different_years(self):
        sheet_form = Form(self.sheet_model.with_user(self.user))
        sheet_form.date_start = date(2019, 12, 29)
        sheet_form.date_end = date(2020, 1, 5)
        self.assertEqual(sheet_form.name, "Weeks 52, 2019 - 01, 2020")
