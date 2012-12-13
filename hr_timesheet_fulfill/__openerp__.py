# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Guewen Baconnier (Camptocamp)
# Author : Vincent Renaville
#
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
	"name" : "Timesheet fullfill wizard",
	"version" : "1.0",
	"author" : "Camptocamp",
	"category" : "Generic Modules/Human Resources",
	"description":
"""
Add a wizard into timesheet allowing people to complete a long period of time with the given values.
This is mainly useful to handle a long period of time like holidays.
Known limitation:
  - Will complete all day between dates
""",
	"website": "http://camptocamp.com",
	"depends" : [
                "hr_timesheet_sheet",
                ],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		            'wizard/timesheet_fulfill_view.xml',
	],
	"active": False,
	'installable': False
}
