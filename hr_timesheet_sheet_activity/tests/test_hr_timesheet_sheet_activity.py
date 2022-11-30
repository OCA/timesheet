# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import fields
from odoo.tests import common


class TestHrTimesheetSheetActivity(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.IrModel = self.env["ir.model"]
        self.ResUsers = self.env["res.users"]
        self.Company = self.env["res.company"]
        self.Project = self.env["project.project"]
        self.HrEmployee = self.env["hr.employee"]
        self.HrTimesheetSheet = self.env["hr_timesheet.sheet"]
        self.AccountAnalyticLine = self.env["account.analytic.line"]
        self.MailActivity = self.env["mail.activity"]
        self.company_id = self.env.ref("base.main_company")
        self.now = fields.Datetime.now()
        self.group_hr_user = self.env.ref("hr.group_hr_user")
        self.group_hr_timesheet_user = self.env.ref(
            "hr_timesheet.group_hr_timesheet_user"
        )
        self.group_project_user = self.env.ref("project.group_project_user")
        self.hr_timesheet_sheet_modelid = self.IrModel._get(
            self.HrTimesheetSheet._name
        ).id
        self.activity_sheet_submission = self.env.ref(
            "hr_timesheet_sheet_activity.activity_sheet_submission"
        )
        self.activity_sheet_resubmission = self.env.ref(
            "hr_timesheet_sheet_activity.activity_sheet_resubmission"
        )
        self.activity_sheet_review = self.env.ref(
            "hr_timesheet_sheet_activity.activity_sheet_review"
        )

    def test_activity(self):
        user_1 = self.ResUsers.sudo().create(
            {
                "name": "User 1",
                "login": "user_1",
                "email": "user-1@example.com",
                "company_id": self.company_id.id,
            }
        )
        user_2 = self.ResUsers.sudo().create(
            {
                "name": "User 2",
                "login": "user_2",
                "email": "user-2@example.com",
                "company_id": self.company_id.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.group_hr_user.id,
                            self.group_hr_timesheet_user.id,
                            self.group_project_user.id,
                        ],
                    )
                ],
            }
        )
        employee = self.HrEmployee.create(
            {
                "name": "Employee",
                "user_id": user_1.id,
            }
        )
        self.HrEmployee.create(
            {
                "name": "Officer",
                "user_id": user_2.id,
            }
        )
        project = self.Project.create(
            {
                "name": "Project",
            }
        )

        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "name": "Time Entry",
            }
        )

        sheet = self.HrTimesheetSheet.with_user(user_1).create(
            {
                "employee_id": employee.id,
            }
        )

        activities = self.MailActivity.search(
            [
                ("res_model_id", "=", self.hr_timesheet_sheet_modelid),
                ("user_id", "=", user_1.id),
            ]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.res_id, sheet.id)
        self.assertEqual(activities.activity_type_id, self.activity_sheet_submission)

        sheet.with_user(user_1).action_timesheet_confirm()

        activities = self.MailActivity.search(
            [
                ("res_model_id", "=", self.hr_timesheet_sheet_modelid),
                ("user_id", "=", user_2.id),
            ]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.res_id, sheet.id)
        self.assertEqual(activities.activity_type_id, self.activity_sheet_review)

        sheet.with_user(user_2).action_timesheet_done()

        activities = self.MailActivity.search(
            [
                ("res_model_id", "=", self.hr_timesheet_sheet_modelid),
            ]
        )
        self.assertEqual(len(activities), 0)

        sheet.with_user(user_2).action_timesheet_draft()

        activities = self.MailActivity.search(
            [
                ("res_model_id", "=", self.hr_timesheet_sheet_modelid),
                ("user_id", "=", user_1.id),
            ]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.res_id, sheet.id)
        self.assertEqual(activities.activity_type_id, self.activity_sheet_resubmission)

        sheet.with_user(user_1).action_timesheet_confirm()

        activities = self.MailActivity.search(
            [
                ("res_model_id", "=", self.hr_timesheet_sheet_modelid),
                ("user_id", "=", user_2.id),
            ]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.res_id, sheet.id)
        self.assertEqual(activities.activity_type_id, self.activity_sheet_review)

        sheet.with_user(user_1).action_timesheet_refuse()

        activities = self.MailActivity.search(
            [
                ("res_model_id", "=", self.hr_timesheet_sheet_modelid),
                ("user_id", "=", user_1.id),
            ]
        )
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities.res_id, sheet.id)
        self.assertEqual(activities.activity_type_id, self.activity_sheet_resubmission)

    def test_period_ends_on_workday(self):
        user_1 = self.ResUsers.sudo().create(
            {
                "name": "User 1",
                "login": "user_1",
                "email": "user-1@example.com",
                "company_id": self.company_id.id,
            }
        )
        user_2 = self.ResUsers.sudo().create(
            {
                "name": "User 2",
                "login": "user_2",
                "email": "user-2@example.com",
                "company_id": self.company_id.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.group_hr_user.id,
                            self.group_hr_timesheet_user.id,
                            self.group_project_user.id,
                        ],
                    )
                ],
            }
        )
        employee = self.HrEmployee.create(
            {
                "name": "Employee",
                "user_id": user_1.id,
            }
        )
        self.HrEmployee.create(
            {
                "name": "Officer",
                "user_id": user_2.id,
            }
        )
        project = self.Project.create(
            {
                "name": "Project",
            }
        )

        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "date": date(2020, 2, 7),
                "name": "Time Entry",
            }
        )

        sheet = (
            self.HrTimesheetSheet.with_user(user_1)
            .with_context(
                {
                    "hr_timesheet_sheet_activity_today": date(2020, 2, 7),
                }
            )
            .create(
                {
                    "employee_id": employee.id,
                    "date_start": date(2020, 2, 3),
                    "date_end": date(2020, 2, 7),
                }
            )
        )

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_submission.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 7))

        sheet.with_user(user_1).action_timesheet_confirm()

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_review.id),
                ("user_id", "=", user_2.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 10))

    def test_period_ends_on_weekend(self):
        user_1 = self.ResUsers.sudo().create(
            {
                "name": "User 1",
                "login": "user_1",
                "email": "user-1@example.com",
                "company_id": self.company_id.id,
            }
        )
        user_2 = self.ResUsers.sudo().create(
            {
                "name": "User 2",
                "login": "user_2",
                "email": "user-2@example.com",
                "company_id": self.company_id.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.group_hr_user.id,
                            self.group_hr_timesheet_user.id,
                            self.group_project_user.id,
                        ],
                    )
                ],
            }
        )
        employee = self.HrEmployee.create(
            {
                "name": "Employee",
                "user_id": user_1.id,
            }
        )
        self.HrEmployee.create(
            {
                "name": "Officer",
                "user_id": user_2.id,
            }
        )
        project = self.Project.create(
            {
                "name": "Project",
            }
        )

        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "date": date(2020, 2, 7),
                "name": "Time Entry",
            }
        )

        sheet = (
            self.HrTimesheetSheet.with_user(user_1)
            .with_context(
                {
                    "hr_timesheet_sheet_activity_today": date(2020, 2, 7),
                }
            )
            .create(
                {
                    "employee_id": employee.id,
                    "date_start": date(2020, 2, 3),
                    "date_end": date(2020, 2, 9),
                }
            )
        )

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_submission.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 7))

        sheet.with_user(user_1).action_timesheet_confirm()

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_review.id),
                ("user_id", "=", user_2.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 10))

    def test_period_overdue(self):
        user_1 = self.ResUsers.sudo().create(
            {
                "name": "User 1",
                "login": "user_1",
                "email": "user-1@example.com",
                "company_id": self.company_id.id,
            }
        )
        user_2 = self.ResUsers.sudo().create(
            {
                "name": "User 2",
                "login": "user_2",
                "email": "user-2@example.com",
                "company_id": self.company_id.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.group_hr_user.id,
                            self.group_hr_timesheet_user.id,
                            self.group_project_user.id,
                        ],
                    )
                ],
            }
        )
        employee = self.HrEmployee.create(
            {
                "name": "Employee",
                "user_id": user_1.id,
            }
        )
        self.HrEmployee.create(
            {
                "name": "Officer",
                "user_id": user_2.id,
            }
        )
        project = self.Project.create(
            {
                "name": "Project",
            }
        )

        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "date": date(2020, 1, 31),
                "name": "Time Entry",
            }
        )

        sheet = (
            self.HrTimesheetSheet.with_user(user_1)
            .with_context(
                {
                    "hr_timesheet_sheet_activity_today": date(2020, 2, 7),
                }
            )
            .create(
                {
                    "employee_id": employee.id,
                    "date_start": date(2020, 1, 27),
                    "date_end": date(2020, 2, 2),
                }
            )
        )

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_submission.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 7))

        sheet.with_user(user_1).action_timesheet_confirm()

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_review.id),
                ("user_id", "=", user_2.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 7))

    def test_weekend_period(self):
        user_1 = self.ResUsers.sudo().create(
            {
                "name": "User 1",
                "login": "user_1",
                "email": "user-1@example.com",
                "company_id": self.company_id.id,
            }
        )
        user_2 = self.ResUsers.sudo().create(
            {
                "name": "User 2",
                "login": "user_2",
                "email": "user-2@example.com",
                "company_id": self.company_id.id,
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.group_hr_user.id,
                            self.group_hr_timesheet_user.id,
                            self.group_project_user.id,
                        ],
                    )
                ],
            }
        )
        employee = self.HrEmployee.create(
            {
                "name": "Employee",
                "user_id": user_1.id,
            }
        )
        self.HrEmployee.create(
            {
                "name": "Officer",
                "user_id": user_2.id,
            }
        )
        project = self.Project.create(
            {
                "name": "Project",
            }
        )

        self.AccountAnalyticLine.create(
            {
                "project_id": project.id,
                "employee_id": employee.id,
                "date": date(2020, 2, 1),
                "name": "Time Entry",
            }
        )

        sheet = (
            self.HrTimesheetSheet.with_user(user_1)
            .with_context(
                {
                    "hr_timesheet_sheet_activity_today": date(2020, 2, 1),
                }
            )
            .create(
                {
                    "employee_id": employee.id,
                    "date_start": date(2020, 2, 1),
                    "date_end": date(2020, 2, 1),
                }
            )
        )

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_submission.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 1))

        sheet.with_user(user_1).action_timesheet_confirm()

        activity = self.MailActivity.search(
            [
                ("res_id", "=", sheet.id),
                ("activity_type_id", "=", self.activity_sheet_review.id),
                ("user_id", "=", user_2.id),
            ]
        )
        self.assertEqual(activity.date_deadline, date(2020, 2, 3))
