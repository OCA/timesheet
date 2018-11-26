# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Task Logs: User from Employee',
    'version': '12.0.1.0.0',
    'category': 'Hidden',
    'website': 'https://github.com/OCA/hr-timesheet',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Sets user according to the employee of a timesheet entry',
    'depends': [
        'hr_timesheet',
        'web_ir_actions_act_view_reload',
    ],
    'data': [
        'views/account_analytic_line.xml',
    ],
}
