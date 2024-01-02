# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class SaleTimesheetOrderLineNoUpdate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.user_type_payable = cls.env.ref("account.data_account_type_payable")
        cls.user_type_receivable = cls.env.ref("account.data_account_type_receivable")
        cls.Partner = cls.env["res.partner"]
        cls.Employee = cls.env["hr.employee"]
        cls.AccountAccount = cls.env["account.account"]
        cls.Project = cls.env["project.project"]
        cls.ProjectTask = cls.env["project.task"]
        cls.AccountAnalyticLine = cls.env["account.analytic.line"]
        cls.ProductProduct = cls.env["product.product"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]

    def test_sale_timesheet_order_line_sync(self):
        project = self.Project.create(
            {"name": "Project #1", "allow_timesheets": True, "allow_billable": True}
        )
        product1 = self.ProductProduct.create(
            {
                "name": "Service #1",
                "standard_price": 30,
                "list_price": 90,
                "type": "service",
                "invoice_policy": "delivery",
                "uom_id": self.uom_hour.id,
                "uom_po_id": self.uom_hour.id,
                "default_code": "CODE-1",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "project_id": project.id,
                "taxes_id": False,
            }
        )
        product2 = self.ProductProduct.create(
            {
                "name": "Service #2",
                "standard_price": 50,
                "list_price": 99,
                "type": "service",
                "invoice_policy": "delivery",
                "uom_id": self.uom_hour.id,
                "uom_po_id": self.uom_hour.id,
                "default_code": "CODE-2",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "project_id": project.id,
                "taxes_id": False,
            }
        )
        employee = self.Employee.create({"name": "Employee #1", "timesheet_cost": 42})
        employee2 = self.Employee.create({"name": "Employee #2", "timesheet_cost": 45})
        account_payable = self.AccountAccount.create(
            {
                "code": "AP4",
                "name": "Payable #1",
                "user_type_id": self.user_type_payable.id,
                "reconcile": True,
            }
        )
        account_receivable = self.AccountAccount.create(
            {
                "code": "AR1",
                "name": "Receivable #1",
                "user_type_id": self.user_type_receivable.id,
                "reconcile": True,
            }
        )
        partner = self.Partner.create(
            {
                "name": "Partner #1",
                "email": "partner1@localhost",
                "property_account_payable_id": account_payable.id,
                "property_account_receivable_id": account_receivable.id,
            }
        )
        sale_order = self.SaleOrder.create(
            {
                "partner_id": partner.id,
                "partner_invoice_id": partner.id,
                "partner_shipping_id": partner.id,
            }
        )
        sale_order_line1 = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "name": product1.name,
                "product_id": product1.id,
                "product_uom_qty": 0,
                "product_uom": self.uom_hour.id,
                "price_unit": product1.list_price,
            }
        )
        sale_order_line2 = self.SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "name": product2.name,
                "product_id": product2.id,
                "product_uom_qty": 0,
                "product_uom": self.uom_hour.id,
                "price_unit": product2.list_price,
            }
        )
        sale_order.action_confirm()
        task = self.ProjectTask.search([("sale_line_id", "=", sale_order_line1.id)])
        timesheet1 = self.AccountAnalyticLine.create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Entry #1-1",
                "unit_amount": 1,
                "employee_id": employee.id,
            }
        )
        self.assertEqual(timesheet1.so_line, sale_order_line1)
        timesheet1._onchange_task_id_employee_id()
        self.assertEqual(timesheet1.so_line, sale_order_line1)
        task.new_sale_line_id = sale_order_line2
        timesheet2 = self.AccountAnalyticLine.create(
            {
                "project_id": task.project_id.id,
                "task_id": task.id,
                "name": "Entry #1-2",
                "unit_amount": 1,
                "employee_id": employee.id,
            }
        )
        self.assertIsNotNone(timesheet2.so_line)
        computed_so_id = timesheet2._timesheet_determine_sale_line(
            task, employee, project
        )
        self.assertEqual(computed_so_id, sale_order_line2)
        timesheet1.employee_id = employee2
        timesheet1._onchange_task_id_employee_id()
        self.assertEqual(timesheet1.so_line, sale_order_line2)
        project.select_all_project_sale_items = False
        project._compute_sale_line_id_domain()
        self.assertIn("order_partner_id", str(project.sale_line_id_domain))
        project.select_all_project_sale_items = True
        project._compute_sale_line_id_domain()
        self.assertIn("order_id", str(project.sale_line_id_domain))
        project.sale_line_id = sale_order_line2
        self.assertEqual(
            project.task_ids[0].new_sale_line_id.id, project.sale_line_id.id
        )
