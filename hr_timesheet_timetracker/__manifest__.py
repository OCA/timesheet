# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Timesheet Timetracker',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/timesheet',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Track time spent using Start/Stop button',
    'depends': [
        'hr_timesheet',
        'web_ir_actions_act_multi',
        'web_ir_actions_act_view_reload',
        'web_notify',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/project_task.xml',
        'views/project_project.xml',
        'views/res_config_settings.xml',
        'views/hr_timesheet_timetracker.xml',
    ],
}
