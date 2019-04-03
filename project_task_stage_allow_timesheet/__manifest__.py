# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Task Stage Allow Timesheet',
    'summary': """
        Allows to tell that a task stage is opened for timesheets.""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), ACSONE SA/NV',
    'website': 'https://github.com/OCA/hr-timesheet',
    'depends': [
        'hr_timesheet',
        'project',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/project_task_type.xml',
    ],
    'demo': [
    ],
}
