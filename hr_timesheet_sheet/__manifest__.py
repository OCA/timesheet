# Copyright 2018 Eficent
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2018-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR Timesheet Sheet',
    'version': '12.0.3.7.2',
    'category': 'Human Resources',
    'sequence': 80,
    'summary': 'Timesheet Sheets, Activities',
    'license': 'AGPL-3',
    'author': (
        'Eficent, '
        'Onestein, '
        'Brainbean Apps, '
        'Odoo Community Association (OCA)'
    ),
    'website': 'https://github.com/OCA/timesheet',
    'installable': True,
    'auto_install': False,
    'depends': [
        'hr_timesheet',
        'web_widget_x2many_2d_matrix',
    ],
    'data': [
        'data/hr_timesheet_sheet_data.xml',
        'security/ir.model.access.csv',
        'security/hr_timesheet_sheet_security.xml',
        'views/hr_timesheet_sheet_views.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_views.xml',
        'views/account_analytic_line_views.xml',
        'views/res_config_settings_views.xml',
        'templates/assets.xml',
    ],
}
