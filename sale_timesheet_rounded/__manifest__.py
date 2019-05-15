# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    'name': 'Sale Timesheet Rounded',
    'summary': 'Round timesheet entries amount based on project settings.',
    'version': '12.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Sales',
    'website': 'https://github.com/OCA/timesheet',
    'depends': [
        'project',
        'hr_timesheet',
        'sale_timesheet',
    ],
    'data': [
        # Views
        'views/account_analytic_line.xml',
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    'installable': True,
}
