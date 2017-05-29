# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet No Closed Project-Task",
    'summary': """
        Prevent to select closed project or task on timesheet line""",
    "version": "10.0.1.0.0",
    "author": "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr-timesheet",
    "category": "Human Resources",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet",
        "hr_timesheet_task",
        "project_stage_closed",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/account_analytic_line.xml',
        'views/hr_timesheet_sheet_sheet.xml',
        'views/hr_timesheet_no_closed_project_task.xml',
    ],
}
