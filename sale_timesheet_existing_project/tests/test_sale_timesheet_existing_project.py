# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestSaleTimesheetExistingProject(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['project.project'].create({
            'name': 'Test project'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test service product',
            'type': 'service',
            'service_tracking': 'task_in_project',
            'project_template_id': cls.project.id,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'project_id': cls.project.id,
        })
        cls.line = cls.env['sale.order.line'].create({
            'order_id': cls.order.id,
            'product_id': cls.product.id,
        })

    def test_onchange_product_service_tracking(self):
        self.product.project_id = self.project.id
        self.product._onchange_service_tracking()
        self.assertFalse(self.product.project_id)
        tmpl = self.product.product_tmpl_id
        tmpl.project_id = self.project.id
        tmpl._onchange_service_tracking()
        self.assertFalse(tmpl.project_id)

    def test_sale_timesheet_existing_project(self):
        self.assertTrue(self.order.visible_project)
        self.order._action_confirm()
        self.assertEqual(self.line.project_id, self.project)
        self.assertEqual(self.line.task_id.project_id, self.project)

    def test_sale_timesheet_existing_project_several_lines(self):
        line2 = self.line.copy({'order_id': self.order.id})
        self.order._action_confirm()
        self.assertEqual(self.line.project_id, self.project)
        self.assertEqual(line2.project_id, self.project)

    def test_sale_timesheet_project_template(self):
        self.order.project_id = False
        self.order._action_confirm()
        self.assertNotEqual(self.line.project_id, self.project)
        self.assertNotEqual(self.line.task_id.project_id, self.project)
        self.assertIn(self.project.name, self.line.project_id.name)

    def test_sale_timesheet_new_project(self):
        self.order.project_id = False
        self.product.project_template_id = False
        line2 = self.line.copy({'order_id': self.order.id})
        self.order._action_confirm()
        self.assertNotEqual(self.line.project_id, self.project)
        self.assertNotEqual(self.line.task_id.project_id, self.project)
        self.assertIn(self.order.name, self.line.project_id.name)
        self.assertEqual(line2.project_id, self.line.project_id)
