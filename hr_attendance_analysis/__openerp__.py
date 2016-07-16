# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "HR - Attendance Analysis",
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'summary': "Dynamic reports based on employee's attendances and "
               "contract's calendar",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'hr_attendance',
        'hr_contract',
        'hr_holidays',
        'report_webkit'
    ],
    "data": [
        'company_view.xml',
        'hr_attendance_view.xml',
        'reports.xml',
        'wizard/print_calendar_report.xml',
        'resource_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": [
        'hr_attendance_demo.xml',
    ],
    "test": [
        'test/attendances.yml',
    ],
    "installable": False
}
