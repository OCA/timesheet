# -*- coding: utf-8 -*-
# Copyright 2016 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Timesheet Holiday',
    'version': '10.0.2.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """When holidays are granted, add lines to the analytic account
        that is linked to the Leave Type""",
    'author': "Sunflower IT, Therp BV, ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/hr-timesheet',
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet_sheet',
        'hr_holidays',
        'hr_holidays_settings',
    ],
    'data': [
        'views/project_config_settings.xml',
        'views/hr_holidays_view.xml',
        'views/company_view.xml',
    ],
    'installable': True
}
