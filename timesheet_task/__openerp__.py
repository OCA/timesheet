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
{'name' : 'Analytic Task',
 'version' : '0.2',
 'author' : 'Camptocamp',
 'maintainer': 'Camptocamp - Acsone SA/NV',
 'category': 'Human Resources',
 'depends' : ['project', 'hr_timesheet_invoice'],
 'description': """
    Replace task work items (project.task.work) linked to task with timesheet lines (hr.analytic.timesheet). 
    This allow to have only one single object that handle and record time spent by employees, making more coherence
    for the end user. This way, time entred through timesheet lines or task is the same. As long as a timesheet lines
    has an associated task, it will compute the related indicators.
    Used with the module hr_timesheet_task, it also allow users to complete task information through the 
    timesheet sheet (hr.timesheet.sheet).
    """,
 'website': 'http://www.camptocamp.com',
 'data': ['project_task_view.xml'],
 'demo': [],
 'test': ['test/task_timesheet_indicators.yml'],
 'installable': True,
 'images' : [],
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True,
}
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
