# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Task Logs Utilization Report',
    'version': '12.0.1.0.1',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr-timesheet',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Generate Utilization Report from Task Logs',
    'depends': [
        'hr_timesheet',
        'report_xlsx',
    ],
    'data': [
        'views/hr_department.xml',
        'views/hr_employee.xml',
        'report/hr_utilization_report.xml',
        'wizards/hr_utilization_report_wizard.xml',
    ],
}
