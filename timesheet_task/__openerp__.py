# -*- coding: utf-8 -*-
# Copyright 2013 Nicolas Bessi, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Analytic Timesheet In Task',
 'version': '8.0.1.0.0',
 'author': "Camptocamp, Daniel Reis, Odoo Community Association (OCA)",
 'category': 'Human Resources',
 'depends': [
     'project',
     'project_timesheet',
     'hr_timesheet_invoice',
     ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'project_task_view.xml',
     'project_task_data.xml',
     'report/hr_timesheet_report_view.xml'
     ],
 'test': ['test/task_timesheet_indicators.yml'],
 'installable': True,
 'license': 'AGPL-3',
 'application': True,
 }
