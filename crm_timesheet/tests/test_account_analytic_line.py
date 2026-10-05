# Copyright 2017 tecnativa - Jairo Llopis
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2025 Tecnativa - Víctor Martínez
# Copyright 2026 Studio73 - Pablo Cortés
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import new_test_user
from odoo.tests.common import users

from odoo.addons.base.tests.common import BaseCommon


class AccountAnalyticLineCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="hr_timesheet.group_hr_timesheet_user,"
            "project.group_project_manager,"
            "sales_team.group_sale_salesman_all_leads",
        )
        cls.user.action_create_employee()
        cls.project = (
            cls.env["project.project"]
            .with_user(cls.user)
            .create({"name": "Test project", "allow_timesheets": True})
        )
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

    def test_onchange_lead(self):
        """Changing the lead changes the associated project."""
        line = self.env["account.analytic.line"].new({"lead_id": self.lead.id})
        line._onchange_lead_id()
        self.assertEqual(line.project_id, self.project)

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
