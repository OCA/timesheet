# -*- coding: utf-8 -*-
# See README.rst file on addon root folder for license details

{
    'name': "CRM Timesheet",
    'category': 'Customer Relationship Management',
    'version': '8.0.1.0.0',
    'depends': [
        'crm',
        'hr_timesheet'
    ],
    'data': [
        'views/crm_lead_view.xml',
        'views/crm_phonecall_view.xml',
        'views/hr_analytic_timesheet_view.xml'
    ],
    'author': 'Antiun Ingeniería S.L.,Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'license': 'AGPL-3',
    'installable': True,
}
