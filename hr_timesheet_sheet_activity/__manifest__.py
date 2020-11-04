# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Timesheet Sheet Activities',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': (
        'Automatic activities related to submission and review of timesheet'
        ' sheets'
    ),
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': [
        'data/hr_timesheet_sheet_activity_data.xml',
        'views/mail_activity.xml',
    ],
}
