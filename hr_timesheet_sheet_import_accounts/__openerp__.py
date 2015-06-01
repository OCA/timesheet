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
    'name': 'Timesheet import accounts from last timesheet',
    'version': '1.0',
    'author': 'Eficent',
    'category': 'Human Resources',
    'description': """
Timesheet import accounts from last timesheet
========================================
It is usual for employees in a company to work on the same projects for weeks.

Completing the timesheets id Odoo currently means entering for each timesheet
the analytic accounts every time, which turns to be time consuming.

This module lets the user import the analytic accounts from the previous
timesheet, with a simple click.


    """,
    'website': 'http://www.eficent.com',
    'depends': ['hr_timesheet_sheet'],
    'data': [
        'view/hr_timesheet_sheet_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
