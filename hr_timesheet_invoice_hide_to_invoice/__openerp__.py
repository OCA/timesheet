# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "HR Timesheet Invoice Hide To Invoice",

    'summary': """
        Adding a security group to display invoicing rate field on timesheet
        line""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Invoicing & Payments',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet_invoice',
        'hr_timesheet_sheet',
    ],
    'data': [
        'security/hr_timesheet_invoice_hide_to_invoice_security.xml',
        'views/hr_timesheet_invoice_hide_to_invoice_view.xml',
    ],
}
