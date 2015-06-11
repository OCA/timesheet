# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Yannick Vaucher (Camptocamp)
#             Vincent Renaville (Camptocamp)
#    Copyright 2013 Camptocamp SA
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
{'name': 'Timesheet improvements',
 'version': '0.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'Human Resources',
 'depends': ['hr_timesheet_sheet'],
 'description': """
 Modifies timesheet behavior:
 - Ensure a DESC order on timesheet lines
 - Set default date for manually entering attendance to max attendance date
 - Redefine constraint on timesheets to check alternation of 'sign in' and
   'sign out' only on current timesheet instead of doing it on all timesheets
   of the employee
 """,
 'website': 'http://www.camptocamp.com',
 'data': ['hr_timesheet_view.xml'],
 'js': [],
 'css': [],
 'qweb': [],
 'demo': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 }
