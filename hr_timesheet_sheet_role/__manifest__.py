# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Timesheet Sheet by Role',
    'version': '12.0.2.2.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr-timesheet',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': (
        'Track time on project according to the role assigned via My Timesheet'
        ' Sheets'
    ),
    'depends': [
        'hr_timesheet_role',
        'hr_timesheet_sheet',
    ],
    'data': [
        'views/hr_timesheet_sheet.xml'
    ],
}
