# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Timesheet Sheet Auto-draft: Project',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Support per-project Timesheet Sheets auto-drafting.',
    'depends': [
        'hr_timesheet_sheet',
        'hr_timesheet_sheet_policy_project_manager',
    ],
}
