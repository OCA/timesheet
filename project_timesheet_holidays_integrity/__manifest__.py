# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Timesheets from Leaves: data integrity',
    'version': '12.0.1.0.1',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Ensures and restores integrity of Leaves and Timesheets data',
    'depends': [
        'project_timesheet_holidays',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/hr_leave.xml',
    ],
}
