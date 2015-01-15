# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Eficent <contact@eficent.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Timesheet validators',
    'version': '1.0',
    'author': 'Eficent',
    'category': 'Human Resources',
    'description': """
Timesheet validators
========================================

Timesheets in Odoo can be validated by users belonging to the group
“Human Resources / Officer”.

However it is frequent for companies allow to employees outside of the
Human Resources group to validate timesheet.

This module allows a user outside of the Human Resources groups to validate
timesheets. A rule is predefined, but it is flexible enough to accept
extensions.

At the time when a user submits a timesheet to the Manager, the application
determines the validators.

Only those validators or employees in the group of Human Resources Officer
are capable of approving the timesheet.

The current rule sets as validators of a timesheet:

- The head of the department that the employee belongs to

In case that the employee is head of the department, it will attempt to add
the head of the parent department instead.

- The employee’s direct manager

The list of validators is visible in the employee’s timesheet.

    """,
    'website': 'http://www.eficent.com',
    'depends': ['hr_timesheet_sheet'],
    'data': [
        'security/hr_timesheet_sheet_security.xml',
        'view/hr_timesheet_sheet_view.xml',
        'view/hr_timesheet_workflow.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}