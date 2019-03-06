# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Timesheet Sheet No Negative',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Negative hours are not admitted.',
    'license': 'AGPL-3',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr-timesheet',
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
