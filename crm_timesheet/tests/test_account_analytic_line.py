# Copyright 2017 tecnativa - Jairo Llopis
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import exceptions, fields
from odoo.tests.common import users

from odoo.addons.project_timesheet_time_control.tests import (
    test_project_timesheet_time_control,
)


class AccountAnalyticLineCase(
    test_project_timesheet_time_control.TestProjectTimesheetTimeControlBase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user.groups_id |= cls.env.ref("sales_team.group_sale_salesman_all_leads")
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
        self.lead.button_end_work()
        # No more running lines, cannot stop again
        with self.assertRaises(exceptions.UserError):
            self.lead.button_end_work()
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
