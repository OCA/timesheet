# -*- coding: utf-8 -*-
##############################################################################
#
# @author Bessi Nicolas
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
	"name" : "Import holidays in timesheets",
	"version" : "1.0",
	"author" : "Camptocamp",
	"category" : "Generic Modules/Human Resources",
	"description":
"""
Wizard to import holidays in the current timesheet.
This module adds a relation between the Leave Types and the Analytic Accounts.
The Timesheet lines are created on the Analytic Account defined on the Leave Type.

The hours to input per day is configurable at company level.
    
Limitations:
  - Consider that the work days are Monday to Friday
  - The wizard creates the attendances each day with Sign-ins at 00:00 and Sign-outs at (00:00 + configured timesheet hours per day).

""",
	"website": "http://www.camptocamp.com",
	"depends" : ["hr",
                 "account",
                 "hr_holidays",
                 "hr_timesheet_sheet"],
	"init_xml" : [],
	"update_xml" : [
		'hr_holidays_view.xml',
        'wizard/holidays_import_view.xml',
        'company_view.xml',
	],
	"active": False,
	'installable': False
}
