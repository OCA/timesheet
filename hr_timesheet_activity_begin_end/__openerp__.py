# -*- coding: utf-8 -*-
# © 2015 Camptocamp SA (author: Guewen Baconnier)
# © 2017 Martronic SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': 'Timesheet Activities - Begin/End Hours',
 'version': '9.0.1.0.0',
 'author': 'Camptocamp,Martronic SA,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Human Resources',
 'depends': [
     'hr_timesheet_sheet',
     'float_time_hms',
     ],
 'website': 'http://www.camptocamp.com',
 'data': ['views/hr_analytic_timesheet.xml',
          'views/hr_timesheet_sheet.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
