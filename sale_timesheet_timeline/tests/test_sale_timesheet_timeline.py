# Copyright 2024 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields
from odoo.tests import Form, new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestSaleTimesheetTimeline(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.user = new_test_user(cls.env, login="test_user_st_timeline")
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "allow_billable": True}
        )
        cls.product_task = cls.env["product.product"].create(
            {
                "name": "Test task product",
                "detailed_type": "service",
                "service_tracking": "task_global_project",
                "service_policy": "ordered_prepaid",
                "project_id": cls.project.id,
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
            }
        )
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_task
            line_form.product_uom_qty = 10
            line_form.name = "This is a long description\nwith line feed"
            line_form.task_date_start = "2024-08-01 00:00:00"
            line_form.task_date_end = "2024-08-05 12:00:00"
            line_form.task_user_ids.add(cls.user)
        cls.order = order_form.save()

    def test_task_creation(self):
        self.order.action_confirm()
        task = self.project.task_ids
        self.assertEqual(
            task.planned_date_start, fields.Datetime.from_string("2024-08-01 00:00:00")
        )
        self.assertEqual(
            task.planned_date_end, fields.Datetime.from_string("2024-08-05 12:00:00")
        )
        self.assertEqual(task.date_deadline, fields.Date.from_string("2024-08-05"))
        self.assertEqual(task.user_ids, self.user)
