# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet No Closed Project-Task",
    'summary': """
        Prevent to select closed project or task on timesheet line""",
    "version": "8.0.1.0.0",
    "author": "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    "website": "http://www.acsone.eu",
    "category": "Human Resources",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet_task",
        "hr_timesheet_invoice",
        "account_analytic_project",
        "project_stage_closed",
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/hr_timesheet_no_closed_project_task_security.xml',
        'views/hr_analytic_timesheet_view.xml',
        'views/hr_timesheet_sheet_view.xml',
        'views/project_task_view.xml',
        'views/hr_timesheet_no_closed_project_task.xml',
    ],
}
