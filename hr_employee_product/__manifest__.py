# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

{
    'name': "Manage products representing employees",
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'author': "Eficent, Odoo Community Association (OCA)",
    'website': 'http://www.github.com/OCA/hr-timesheet',
    'license': 'AGPL-3',
    'summary': 'Product is an employee',
    "depends": ['product', 'hr_timesheet'],
    "data": [
        'security/product_security.xml',
        'view/product.xml'
    ],
    "installable": True
}
