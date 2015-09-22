# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Arnaud Wüst (Camptocamp)
#    Author: Nicolas Bessi (Camptocamp)
#    Author: Guewen Baconnier (Camptocamp) (port to v7)
#    Copyright 2011-2012 Camptocamp SA
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
    "name": "Timesheet Reminder",
    "version": "2.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": 'AGPL-3',
    "category": "",
    "website": "http://www.camptocamp.com",
    "description": """
Timesheet Reports Module
========================

 * Add a menu in `Human Resources / Configuration
   / Timesheet Reminder`.
   It allows to send automatic emails to those who did
   not complete their timesheet in the last 5 weeks.
 * Per employee, you can choose to send the reminder or not.
 * Add a report in `Human Resources / Reporting / Timesheet
   / Timesheet Status` which displays the state of the last
   5 timesheets for all users per company.

This module replaces the modules c2c_timesheet_reports
of TinyERP 4 and OpenERP 5.
    """,
    "depends": ["hr_timesheet_sheet"],
    "init_xml": [],
    "update_xml": [
        'security/ir.model.access.csv',
        'wizard/reminder_config_view.xml',
        'wizard/reminder_status_view.xml',
        'hr_employee_view.xml',
        'timesheet_report.xml',
    ],
    "active": False,
    'installable': False
}
