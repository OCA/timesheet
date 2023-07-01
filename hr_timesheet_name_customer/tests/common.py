# Copyright 2023-nowdays Cetmix OU (https://cetmix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests.common import TransactionCase


class TestCommonNameCustomer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestCommonNameCustomer, cls).setUpClass()

        # customer partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Customer For Analytic Account",
                "email": "customer@task.com",
                "phone": "42",
            }
        )

        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Plan Test",
                "company_id": False,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Account for Test Customer",
                "partner_id": cls.partner.id,
                "plan_id": cls.analytic_plan.id,
                "code": "TEST",
            }
        )

        # project and tasks
        cls.project_customer = cls.env["project.project"].create(
            {
                "name": "Project X",
                "allow_timesheets": True,
                "partner_id": cls.partner.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.task1 = cls.env["project.task"].create(
            {
                "name": "Task One",
                "priority": "0",
                "kanban_state": "normal",
                "project_id": cls.project_customer.id,
                "partner_id": cls.partner.id,
            }
        )
        cls.task2 = cls.env["project.task"].create(
            {
                "name": "Task Two",
                "priority": "1",
                "kanban_state": "done",
                "project_id": cls.project_customer.id,
            }
        )
        # users
        cls.user_employee = cls.env["res.users"].create(
            {
                "name": "User Employee",
                "login": "user_employee",
                "email": "useremployee@test.com",
                "groups_id": [
                    (6, 0, [cls.env.ref("hr_timesheet.group_hr_timesheet_user").id])
                ],
            }
        )

        # employees
        cls.empl_employee = cls.env["hr.employee"].create(
            {
                "name": "User Empl Employee",
                "user_id": cls.user_employee.id,
            }
        )
