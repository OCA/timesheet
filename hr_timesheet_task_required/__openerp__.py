# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Timesheet Task Required',
    'summary': """
        Set task on timesheet as a mandatory field""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'www.acsone.eu',
    'depends': [
        'hr_timesheet_task',
    ],
    'data': [
        'views/hr_timesheet_task_required.xml',
        'views/hr_timesheet_view.xml',
    ],
}
