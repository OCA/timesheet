# Copyright 2017 tecnativa - Jairo Llopis
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2025 Tecnativa - Víctor Martínez
# Copyright 2026 Studio73 - Pablo Cortés
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import exceptions, fields
from odoo.tests.common import users

from odoo.addons.hr_timesheet_time_control.tests import (
    test_project_timesheet_time_control,
)


class AccountAnalyticLineCase(
    test_project_timesheet_time_control.TestProjectTimesheetTimeControlBase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user.group_ids |= cls.env.ref("sales_team.group_sale_salesman_all_leads")
        cls.lead = (
            cls.env["crm.lead"]
            .with_user(cls.user)
            .create(
                {
                    "name": "Test lead",
                    "project_id": cls.project.id,
                }
            )
        )
        cls.line.lead_id = cls.lead

    def test_onchange_lead(self):
        """Changing the lead changes the associated project."""
        line = self.env["account.analytic.line"].new({"lead_id": self.lead.id})
        line._onchange_lead_id()
        self.assertEqual(line.project_id, self.project)

    def test_aal_time_control_flow(self):
        """Test account.analytic.line time controls."""
        resume_action = self.line.button_resume_work()
        wizard = self._create_wizard(resume_action, self.line)
        self.assertEqual(wizard.analytic_line_id, self.line)
        self.assertEqual(wizard.project_id, self.line.project_id)
        # Stop old timer, start new one
        new_act = wizard.with_context(show_created_timer=True).action_switch()
        new_line = self.env[new_act["res_model"]].browse(new_act["res_id"])
        self.assertEqual(new_line.lead_id, self.lead)

    @users("test-user")
    def test_lead_time_control_flow(self):
        """Test crm.lead time controls."""
        # Running line found, stop the timer
        self.assertEqual(self.lead.show_time_control, "stop")
        # Button_end_work returns a wizard action
        action = self.lead.button_end_work()
        self.assertEqual(action["res_model"], "hr.timesheet.stop")
        # Execute the wizard to stop work
        wizard = (
            self.env["hr.timesheet.stop"]
            .with_context(**action["context"])
            .create({"name": "Finished work"})
        )
        wizard.action_stop()
        # No more running lines, cannot stop again
        with self.assertRaises(exceptions.UserError):
            self.lead.with_context(skip_stop_wizard=True).button_end_work()
        # All lines stopped, start new one
        self.assertEqual(self.lead.show_time_control, "start")
        start_action = self.lead.button_start_work()
        wizard = self._create_wizard(start_action, self.lead)
        self.assertLessEqual(wizard.date_time, fields.Datetime.now())
        self.assertEqual(
            wizard.analytic_line_id.account_id, self.lead.project_id.account_id
        )
        self.assertEqual(wizard.name, self.line.name)
        self.assertEqual(wizard.project_id, self.lead.project_id)
        new_act = wizard.with_context(show_created_timer=True).action_switch()
        new_line = self.env[new_act["res_model"]].browse(new_act["res_id"])
        self.assertEqual(new_line.employee_id, self.env.user.employee_ids)
        self.assertEqual(new_line.project_id, self.project)
        self.assertEqual(new_line.lead_id, self.lead)

    @users("test-user")
    def test_total_time_spent(self):
        """Test crm.lead total_time_spent computation."""
        current_total = self.lead.total_time_spent
        self.env["account.analytic.line"].create(
            {
                "name": "Test line 1",
                "project_id": self.project.id,
                "lead_id": self.lead.id,
                "unit_amount": 2.5,
                "employee_id": self.env.user.employee_id.id,
            }
        )
        self.lead.invalidate_recordset(["total_time_spent"])
        self.assertEqual(self.lead.total_time_spent, current_total + 2.5)
        self.env["account.analytic.line"].create(
            {
                "name": "Test line 2",
                "project_id": self.project.id,
                "lead_id": self.lead.id,
                "unit_amount": 1.5,
                "employee_id": self.env.user.employee_id.id,
            }
        )
        self.lead.invalidate_recordset(["total_time_spent"])
        self.assertEqual(self.lead.total_time_spent, current_total + 4.0)

    def test_team_project_defaulting(self):
        """Test that project_id is inherited from team_id."""
        team = self.env["crm.team"].create(
            {
                "name": "Test Team",
                "timesheet_project_id": self.project.id,
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Team Lead",
                "team_id": team.id,
            }
        )
        self.assertEqual(lead.project_id, self.project)

    def test_team_project_already_has_project(self):
        """Test that project_id is NOT overwritten if already set."""
        team = self.env["crm.team"].create(
            {
                "name": "Another Test Team",
                "timesheet_project_id": self.project.id,
            }
        )
        lead = self.env["crm.lead"].create(
            {
                "name": "Lead with Project",
                "project_id": self.project.id,
            }
        )
        lead.team_id = team
        self.assertEqual(lead.project_id, self.project)

    @users("test-user")
    def test_hr_timesheet_switch_coverage(self):
        """Test hr.timesheet.switch default_get and _closest_suggestion."""
        # Stop existing running timers to avoid "2 running timers found" error
        self.env["account.analytic.line"].search(
            [
                ("employee_id", "in", self.env.user.employee_ids.ids),
                ("unit_amount", "=", 0),
            ]
        ).write({"unit_amount": 1.0})
        # Case 1: No previous timesheets, get project from active_id in context
        lead_no_timesheets = self.env["crm.lead"].create(
            {"name": "No Timesheets", "project_id": self.project.id}
        )
        ctx = {
            "active_model": "crm.lead",
            "active_id": lead_no_timesheets.id,
        }
        wizard = self.env["hr.timesheet.switch"].with_context(**ctx).create({})
        res = wizard.default_get(["project_id"])
        self.assertEqual(res.get("project_id"), self.project.id)
        # Case 2: Closest suggestion from lead_id
        line = self.env["account.analytic.line"].create(
            {
                "name": "Last line",
                "project_id": self.project.id,
                "lead_id": self.lead.id,
                "employee_id": self.env.user.employee_id.id,
            }
        )
        ctx_with_lead = {
            "active_model": "crm.lead",
            "active_id": self.lead.id,
        }
        wizard_with_lead = (
            self.env["hr.timesheet.switch"].with_context(**ctx_with_lead).create({})
        )
        suggestion = wizard_with_lead._closest_suggestion()
        self.assertEqual(suggestion, line)
        # Case 3: No lead in context (lead_id is False)
        wizard_no_ctx = self.env["hr.timesheet.switch"].create({})
        res_no_ctx = wizard_no_ctx.default_get(["project_id"])
        self.assertFalse(res_no_ctx.get("project_id"))
        # Case 4: Lead with no project_id (lead.project_id is False)
        lead_no_project = self.env["crm.lead"].create({"name": "No Project"})
        ctx_no_project = {
            "active_model": "crm.lead",
            "active_id": lead_no_project.id,
        }
        wizard_no_project = (
            self.env["hr.timesheet.switch"].with_context(**ctx_no_project).create({})
        )
        res_no_project = wizard_no_project.default_get(["project_id"])
        self.assertFalse(res_no_project.get("project_id"))
