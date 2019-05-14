# Copyright 2018 ACSONE SA/NV
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project Task Stage Allow Timesheet',
    'summary': """
        Allows to tell that a task stage is opened for timesheets.""",
    'version': '12.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), ACSONE SA/NV',
    'website': 'https://github.com/OCA/timesheet',
    'depends': [
        'hr_timesheet',
        'project',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/project_task_type.xml',
    ],
}
