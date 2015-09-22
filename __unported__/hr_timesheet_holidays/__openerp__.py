# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: JB Aubort
#    Copyright 2008 Camptocamp SA
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

{'name': 'Import holidays in timesheets',
 'version': '1.0',
 'category': 'Generic Modules/Human Resources',
 'description': """
Wizard to import holidays in the current timesheet
==================================================

This module adds a relation between the Leave Types and the Analytic Accounts.
The Timesheet lines are created on the Analytic Account defined on the Leave
Type.

The hours to input per day is configurable at company level.

Limitations:

- Consider that the work days are Monday to Friday
- The wizard creates the attendances each day with Sign-ins at 00:00 and
  Sign-outs at (00:00 + configured timesheet hours per day).

Contributors
------------

* Jean-Baptiste Aubort <jean-baptiste.aubort@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

""",
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'website': 'http://www.camptocamp.com',
 'license': 'AGPL-3',
 'depends': [
     'hr',
     'account',
     'hr_holidays',
     'hr_timesheet_sheet'
 ],
 'data': [
     'hr_holidays_view.xml',
     'wizard/holidays_import_view.xml',
     'company_view.xml',
 ],
 'installable': False,
 'auto_install': False,
 'application': False,
 }
