# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class AccountAnalyticLineCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")
        # Stop any timer running
        cls.env["account.analytic.line"].search(
            [
                ("date_time", "!=", False),
                ("user_id", "=", admin.id),
                ("project_id.allow_timesheets", "=", True),
                ("unit_amount", "=", 0),
            ]
        ).button_end_work()
        admin.groups_id |= (
            cls.env.ref("hr_timesheet.group_hr_timesheet_user")
            | cls.env.ref("sales_team.group_sale_salesman")
            | cls.env.ref("project.group_project_manager")
        )
        env = cls.env(user=admin)
        Account = env["account.analytic.account"]
        Project = env["project.project"]
        cls.analytic_plan = cls.env["account.analytic.plan"].create({"name": "Default"})
        cls.account1 = Account.create(
            {"name": "Test Account 1", "plan_id": cls.analytic_plan.id}
        )
        cls.project1 = Project.create(
            {
                "name": "Test Project 1",
                "analytic_account_id": cls.account1.id,
            }
        )
        cls.lead = env["crm.lead"].create(
            {
                "name": "Test lead",
                "project_id": cls.project1.id,
            }
        )

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
        return (
            active_record.env[action["res_model"]]
            .with_context(
                active_id=active_record.id,
                active_ids=active_record.ids,
                active_model=active_record._name,
                **action.get("context", {}),
            )
            .create({})
        )

    def test_onchange_lead(self):
        """Changing the lead changes the associated project."""
        line = self.env["account.analytic.line"].new(
            {
                "lead_id": self.lead.id,
            }
        )
        line._onchange_lead_id()
        self.assertEqual(line.project_id, self.project1)
