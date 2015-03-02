# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Arnaud Wüst (Camptocamp)
# Author : Nicolas Bessi (Camptocamp)
# Author : Guewen Baconnier (Camptocamp)
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
    "name" : "Timesheet Reminder",
    "version" : "2.0",
    "author" : "Camptocamp,Odoo Community Association (OCA)",
    "category" : "",
    "website" : "http://www.camptocamp.com",
    "description": """
Timesheet Reports Module:
    * Add a menu in Human Resources / Configuration / Timesheet Reminder. It allows to send automatic emails to those who did not complete their timesheet in the last 5 weeks.
    * Per employee, you can choose to send the reminder or not.
    * Add a report in Human Resources / Reporting / Timesheet / Timesheet Status which displays the state of the last 5 timesheets for all users per company.

This module replaces the modules c2c_timesheet_reports in TinyERP 4 and OpenERP 5.
    """,
    "depends" : ["hr_timesheet_sheet"],
    "init_xml" : [],
    "update_xml" : [
        'security/ir.model.access.csv',
        'wizard/reminder_config_view.xml',
        'wizard/reminder_status_view.xml',
        'hr_employee_view.xml',
        'timesheet_report.xml',
    ],
    "active": False,
    "installable": True
}
