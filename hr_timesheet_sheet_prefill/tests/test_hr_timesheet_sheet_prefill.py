# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import Form, new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestTimesheetSheetPrefill(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sheet_model = cls.env["hr_timesheet.sheet"]
        cls.aal_model = cls.env["account.analytic.line"]
        cls.project_model = cls.env["project.project"]
        cls.task_model = cls.env["project.task"]
        cls.company = cls.env.company
        cls.user = new_test_user(
            cls.env,
            login="prefill_user",
            groups="hr_timesheet.group_hr_timesheet_user,project.group_project_user",
            company_id=cls.company.id,
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Prefill Employee",
                "user_id": cls.user.id,
                "company_id": cls.company.id,
            }
        )
        cls.project_1 = cls.project_model.create(
            {"name": "P1", "company_id": cls.company.id, "allow_timesheets": True}
        )
        cls.project_2 = cls.project_model.create(
            {"name": "P2", "company_id": cls.company.id, "allow_timesheets": True}
        )
        cls.task_1 = cls.task_model.create(
            {"name": "T1", "project_id": cls.project_1.id, "company_id": cls.company.id}
        )
        cls.task_2 = cls.task_model.create(
            {"name": "T2", "project_id": cls.project_2.id, "company_id": cls.company.id}
        )

    def _create_sheet(self, date_start, date_end):
        with Form(self.sheet_model.with_user(self.user)) as f:
            f.employee_id = self.employee
            f.date_start = date_start
            f.date_end = date_end
        return f.record

    def _add_timesheet_line(self, sheet, project, task, unit_amount=1.0):
        vals = {
            "project_id": project.id,
            "task_id": task.id,
            "employee_id": self.employee.id,
            "unit_amount": unit_amount,
            "date": sheet.date_start,
            "sheet_id": sheet.id,
        }
        self.aal_model.with_user(self.user).create(vals)

    def _create_current_sheet_with_confirmed_previous(self, combos):
        prev_start = fields.Date.today() - relativedelta(weeks=2)
        prev_end = prev_start + timedelta(days=6)
        prev_sheet = self._create_sheet(prev_start, prev_end)
        for project, task in combos:
            self._add_timesheet_line(prev_sheet, project, task)
        prev_sheet.action_timesheet_confirm()
        self.assertEqual(prev_sheet.state, "confirm")
        cur_start = fields.Date.today() - relativedelta(weeks=1)
        cur_end = cur_start + timedelta(days=6)
        cur_sheet = self._create_sheet(cur_start, cur_end)
        return cur_sheet

    def test_prefill_creates_all_combos_when_sheet_is_empty(self):
        cur_sheet = self._create_current_sheet_with_confirmed_previous(
            combos=[(self.project_1, self.task_1), (self.project_2, self.task_2)]
        )
        cur_sheet.action_prefill_from_previous()
        after = {
            (line.project_id.id, line.task_id.id) for line in cur_sheet.timesheet_ids
        }
        self.assertEqual(len(after), 2)
        self.assertIn((self.project_1.id, self.task_1.id), after)
        self.assertIn((self.project_2.id, self.task_2.id), after)
        self.assertTrue(
            all(line.unit_amount == 0.0 for line in cur_sheet.timesheet_ids)
        )

    def test_prefill_creates_missing_project_task_combos(self):
        cur_sheet = self._create_current_sheet_with_confirmed_previous(
            combos=[(self.project_1, self.task_1), (self.project_2, self.task_2)]
        )
        self._add_timesheet_line(cur_sheet, self.project_1, self.task_1)
        before = {
            (line.project_id.id, line.task_id.id) for line in cur_sheet.timesheet_ids
        }
        self.assertEqual(len(before), 1)
        cur_sheet.action_prefill_from_previous()
        after = {
            (line.project_id.id, line.task_id.id) for line in cur_sheet.timesheet_ids
        }
        self.assertEqual(len(after), 2)
        self.assertIn((self.project_1.id, self.task_1.id), after)
        self.assertIn((self.project_2.id, self.task_2.id), after)

    def test_prefill_raises_if_no_previous_sheet(self):
        start = fields.Date.today() - relativedelta(weeks=1)
        end = start + timedelta(days=6)
        sheet = self._create_sheet(start, end)
        with self.assertRaises(UserError):
            sheet.action_prefill_from_previous()

    def test_prefill_raises_if_nothing_to_create(self):
        cur_sheet = self._create_current_sheet_with_confirmed_previous(
            combos=[(self.project_1, self.task_1)]
        )
        self._add_timesheet_line(cur_sheet, self.project_1, self.task_1)
        with self.assertRaises(UserError):
            cur_sheet.action_prefill_from_previous()

    def test_prefill_raises_if_sheet_not_draft(self):
        cur_sheet = self._create_current_sheet_with_confirmed_previous(
            combos=[(self.project_1, self.task_1)]
        )
        cur_sheet.action_timesheet_confirm()
        self.assertEqual(cur_sheet.state, "confirm")
        with self.assertRaises(UserError):
            cur_sheet.action_prefill_from_previous()
