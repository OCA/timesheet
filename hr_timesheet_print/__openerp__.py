# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, ported by Joel Grand-Guillaume
#    Copyright 2012 Camptocamp SA
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
    "name": "Project Timesheet printing",
    "description": """
This module adds a report on timesheet lines (hr.analytic.timesheet) to print
out the detailed of hours passed.

 """,
    "version": "1.3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "category": "Generic Modules/Projects & Services",
    "website": "http://www.camptocamp.com",
    "license": 'AGPL-3',
    "depends": [
        "analytic",
        "hr_timesheet_invoice",
    ],
    "data": [
        "report.xml",
    ],
    'installable': False
}
