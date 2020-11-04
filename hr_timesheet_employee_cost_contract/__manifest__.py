# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Timesheet: Employee Cost from Contract',
    'version': '12.0.1.0.1',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Compute employee cost from contracts',
    'depends': [
        'hr_timesheet',
        'hr_contract',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/res_config_settings.xml'
    ],
}
