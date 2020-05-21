# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Timesheet Order Line Sync',
    'version': '12.0.1.0.1',
    'category': 'Sales',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'Tecnativa, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Propagate task order line in not invoiced timesheet lines',
    'depends': [
        'sale_timesheet',
    ],
}
