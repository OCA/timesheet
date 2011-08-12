# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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
	"name" : "Timesheet on tasks from Timesheet",
	"version" : "1.0",
	"author" : "Camptocamp",
	"category" : "Generic Modules/Human Resources",
	"module":
"""
This module allow you to enter your timesheet for a specific task and will automatically create a 'work done' entry
in the concerned task. Unless the project_timesheet module, this module base the work done of task on timesheet line 
(hr.analytic.timesheet), so we only have one object for all time recording entry.

It also add some option on filter available for timesheet line and timesheet_sheet.

This module also allow you to modify some field (task_id, description, to_invoice) even if the timesheet is confirmed. This
let the project manager change some values if needed.

Warning: you have to apply project_addons.patch (in the module's root) on the addons branch.
It modifies the sequence of the function fields of the project so they are computed after the function fields of the tasks.
This could not be overidded in this module and is necessary to have all the project indicators correctly computed.

""",
	"website": "http://camptocamp.com",
	"depends" : ["project",
                "hr_timesheet_sheet",
                "hr_timesheet_invoice",
                "project_billing_utils",
                "analytic_multicurrency",
                ],
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		"hr_timesheet_task_view.xml",
        "project_view.xml",
        "hr_timesheet_sheet_view.xml",
        "wizard/wizard_actions.xml",
	],
	"active": False,
	"installable": True
}
