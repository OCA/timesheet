# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Task Logs Timesheet Report',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'maintainers': ['alexey-pelykh'],
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Generate Timesheet Report from Task Logs',
    'depends': [
        'hr_timesheet',
        'report_xlsx',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'report/hr_timesheet_report.xml',
        'wizards/hr_timesheet_report_wizard.xml',
    ],
}
