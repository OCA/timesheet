# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale timesheet invoicing',
    'summary': 'Link timesheet lines to invoice in draft state',
    'version': '11.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Sales',
    'depends': [
        'sale_timesheet',
        'account_cancel',
    ],
    'website': 'https://github.com/OCA/timesheet',
    'installable': True,
}
