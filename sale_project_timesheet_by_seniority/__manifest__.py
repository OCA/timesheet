# Copyright 2019 Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Project Timesheet By Seniority',
    'summary': """
        Automatically map employee and sale order line when timesheeting.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/timesheet',
    'depends': [
        'sale_timesheet',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_seniority_level.xml',
    ],
    'installable': True,
}
