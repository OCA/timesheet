# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Link holidays to analytic lines',
    'version': '8.0.1.1.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """When holidays are granted, add lines to the analytic account
        that is linked to the Leave Type""",
    'author': "Sunflower IT, Therp BV, Odoo Community Association (OCA)",
    'website': 'http://sunflowerweb.nl',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet_sheet',
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_view.xml',
        'views/company_view.xml',
    ],
    'installable': True
}
