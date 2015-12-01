# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "HR Timesheet Invoice Hide To Invoice Task",

    'summary': """
        Hide invoicing rate field on task work""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Invoicing & Payments',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'timesheet_task',
        'hr_timesheet_invoice_hide_to_invoice',
    ],
    'data': [
        'views/hr_timesheet_invoice_hide_to_invoice_task_view.xml',
    ],
    'auto_install': True,
}
