# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sales Timesheet: Hook',
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': (
        'Adds hook points in sale_timesheet module in order to add more'
        'flexibility in the billing types for the creation of Sale Orders'
    ),
    'depends': [
        'sale_timesheet',
    ],
}
