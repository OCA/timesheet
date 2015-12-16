# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_timesheet_no_closed_project_task,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_timesheet_invoice_hide_to_invoice is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_timesheet_invoice_hide_to_invoice is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_timesheet_no_closed_project_task.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "HR Timesheet No Closed Project-Task",
    'summary': """
        Prevent to select closed project or task on timesheet line""",
    "version": "8.0.1.0.0",
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "category": "Human Resources",
    "depends": [
        "hr_timesheet_task",
        "hr_timesheet_invoice",
        "account_analytic_project",
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/hr_timesheet_no_closed_project_task_security.xml',
        'views/hr_analytic_timesheet_view.xml',
        'views/hr_timesheet_sheet_view.xml',
        'views/project_task_view.xml',
        'views/hr_timesheet_no_closed_project_task.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
}
