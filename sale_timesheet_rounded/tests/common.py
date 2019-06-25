# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase


# This class is a backport from odoo 12.0 common test cases in modules account
# and sale with the data needed to run the TestRounded unittest

class TestSaleTimesheetCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetCommon, cls).setUpClass()
        # To speed up test, create object without mail tracking
        context_no_mail = {
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True
        }
        # Create base account to simulate a chart of account
        user_type_payable = cls.env.ref('account.data_account_type_payable')
        cls.account_payable = cls.env['account.account'].create({
            'code': 'NC1110',
            'name': 'Test Payable Account',
            'user_type_id': user_type_payable.id,
            'reconcile': True
        })
        user_type_receivable = cls.env.ref(
            'account.data_account_type_receivable'
        )
        cls.account_receivable = cls.env['account.account'].create({
            'code': 'NC1111',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True
        })
        # Create a customer
        Partner = cls.env['res.partner'].with_context(context_no_mail)
        cls.partner_customer_usd = Partner.create({
            'name': 'Customer from the North',
            'email': 'customer.usd@north.com',
            'customer': True,
            'property_account_payable_id': cls.account_payable.id,
            'property_account_receivable_id': cls.account_receivable.id,
        })
        cls.sale_journal0 = cls.env['account.journal'].create({
            'name': 'Sale Journal',
            'type': 'sale',
            'code': 'SJT0',
        })

    @classmethod
    def setUpEmployees(cls):
        # Create employees
        cls.employee_user = cls.env['hr.employee'].create({
            'name': 'Employee User',
            'timesheet_cost': 15,
        })

    @classmethod
    def setUpServiceProducts(cls):
        """ Create Service product for all kind, with each tracking policy. """
        # Account and project
        cls.account_sale = cls.env['account.account'].create({
            'code': 'SERV-2020',
            'name': 'Product Sales - (test)',
            'reconcile': True,
            'user_type_id': cls.env.ref(
                'account.data_account_type_revenue').id,
        })
        # Create projects
        cls.project_global = cls.env['project.project'].create({
            'name': 'Project for selling timesheets',
            'allow_timesheets': True,
        })
        # Create service products
        uom_hour = cls.env.ref('product.product_uom_hour')
        # -- timesheet on tasks (delivered, timesheet)
        cls.product_delivery_timesheet2 = cls.env['product.product'].create({
            'name': "Service delivered, create task in global project",
            'standard_price': 30,
            'list_price': 90,
            'type': 'service',
            'invoice_policy': 'delivery',
            'uom_id': uom_hour.id,
            'uom_po_id': uom_hour.id,
            'default_code': 'SERV-DELI2',
            'service_type': 'timesheet',
            'service_tracking': 'task_global_project',
            'project_id': cls.project_global.id,
            'taxes_id': False,
            'property_account_income_id': cls.account_sale.id,
        })
