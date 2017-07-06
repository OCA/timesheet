# -*- coding: utf-8 -*-
# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Timesheet Task Required',
    'summary': """
        Set task on timesheet as a mandatory field""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr-timesheet',
    'depends': [
        'hr_timesheet_task',
    ],
    'data': [
        'views/account_analytic_line.xml',
        'views/assets.xml',
        'views/hr_timesheet_sheet.xml',
    ],
}
