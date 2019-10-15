# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, datetime, timedelta
from odoo import exceptions
from odoo.tests.common import SavepointCase


class AccountAnalyticLineCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        admin.groups_id |= (
            cls.env.ref("hr_timesheet.group_hr_timesheet_user") |
            cls.env.ref("sales_team.group_sale_salesman")
        )
        env = cls.env(user=admin)
        Account = env["account.analytic.account"]
        Project = env["project.project"]
        cls.account1 = Account.create({
            "name": "Test Account 1",
        })
        cls.project1 = Project.create({
            "name": "Test Project 1",
            "analytic_account_id": cls.account1.id,
        })
        cls.lead = env['crm.lead'].create({
            'name': 'Test lead',
            'project_id': cls.project1.id,
        })

    def setUp(self):
        super().setUp()
        self.uid = self.ref("base.user_admin")

    def _create_wizard(self, action, active_record):
        """Create a new hr.timesheet.switch wizard in the specified context.

        :param dict action: Action definition that creates the wizard.
        :param active_record: Record being browsed when creating the wizard.
        """
        self.assertEqual(action["res_model"], "hr.timesheet.switch")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["view_type"], "form")
        return active_record.env[action["res_model"]].with_context(
            active_id=active_record.id,
            active_ids=active_record.ids,
            active_model=active_record._name,
            **action.get("context", {}),
        ).create({})

    def test_onchange_lead(self):
        """Changing the lead changes the associated project."""
        line = self.env["account.analytic.line"].new({
            "lead_id": self.lead.id,
        })
        line._onchange_lead_id()
        self.assertEqual(line.project_id, self.project1)

    def test_lead_time_control_flow(self):
        """Test crm.lead time controls."""
        # A timer is running
        previous_line = self.env["account.analytic.line"].create({
            'date_time': datetime.now() - timedelta(hours=1),
            'lead_id': self.lead.id,
            'project_id': self.project1.id,
            'account_id': self.account1.id,
            'name': 'Test line',
        })
        self.assertFalse(previous_line.unit_amount)
        # Running line found, stop the timer
        self.assertEqual(self.lead.show_time_control, "stop")
        self.lead.button_end_work()
        # No more running lines, cannot stop again
        with self.assertRaises(exceptions.UserError):
            self.lead.button_end_work()
        # All lines stopped, start new one
        self.lead.invalidate_cache()
        self.assertEqual(self.lead.show_time_control, "start")
        start_action = self.lead.button_start_work()
        wizard = self._create_wizard(start_action, self.lead)
        self.assertFalse(wizard.amount)
        self.assertLessEqual(wizard.date_time, datetime.now())
        self.assertLessEqual(wizard.date, date.today())
        self.assertFalse(wizard.unit_amount)
        self.assertEqual(
            wizard.account_id,
            self.lead.project_id.analytic_account_id)
        self.assertEqual(wizard.employee_id, self.env.user.employee_ids)
        self.assertEqual(wizard.name, previous_line.name)
        self.assertEqual(wizard.project_id, self.lead.project_id)
        self.assertEqual(wizard.lead_id, self.lead)
        new_act = wizard.with_context(show_created_timer=True).action_switch()
        new_line = self.env[new_act["res_model"]].browse(new_act["res_id"])
        self.assertEqual(new_line.employee_id, self.env.user.employee_ids)
        self.assertEqual(new_line.project_id, self.project1)
        self.assertEqual(new_line.lead_id, self.lead)
        self.assertEqual(new_line.unit_amount, 0)
        self.assertTrue(previous_line.unit_amount)
