# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import common


class TestHrEmployeeProduct(common.TransactionCase):

    def setUp(self):
        super(TestHrEmployeeProduct, self).setUp()
        self.res_users_model = self.env['res.users'].with_context(
            tracking_disable=True, no_reset_password=True)
        self.grp_user = self.env.ref('base.group_user')
        self.grp_hr_manager = self.env.ref('hr.group_hr_manager')
        self.company = self.env.ref('base.main_company')

        self.user1 = self._create_user('user1', [self.grp_user], self.company)
        self.user2 = self._create_user('user2', [self.grp_hr_manager],
                                       self.company)

        self.Product = self.env['product.product']
        self.product_1 = self.Product.create({
            'name': 'Marc',
            'type': 'service',
            'default_code': 'M-1',
            'list_price': 40.0,
            'standard_price': 20.0,
            'is_employee': True
        })

    def _create_user(self, login, groups, company, context=None):
        """ Create a user. """
        group_ids = [group.id for group in groups]
        user = self.res_users_model.create({
            'name': 'Test User',
            'login': login,
            'password': 'demo',
            'email': 'test@yourcompany.com',
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, group_ids)]
        })

        return user

    def test_01_hr_employee_product(self):
        product_list1 = self.Product.sudo(self.user1).\
            search([]).mapped('name')
        product_list2 = self.Product.sudo(self.user2).\
            search([]).mapped('name')

        self.assertLess(len(product_list1), len(product_list2), 'User1 should'
                        'have less products in the list')
