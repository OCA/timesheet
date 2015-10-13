# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
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
{'name': 'Task in time sheet',
 'version': '8.0.0.3.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp - Acsone SA/NV',
 'category': 'Human Resources',
 'depends': ['timesheet_task', 'hr_timesheet_sheet'],
 'description': """Replace project.task.work items linked to task
                   with hr.analytic.timesheet""",
 'website': 'http://www.camptocamp.com',
 'data': ['hr_timesheet_sheet_view.xml',
          'hr_analytic_timesheet_view.xml',
          'hr_timesheet_task.xml'],
 'qweb': ['static/src/xml/timesheet.xml'],
 'demo': [],
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
 }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
