# -*- coding: utf-8 -*-
# Copyright 2015 Camptocamp SA - Guewen Baconnier
# Copyright 2017 Tecnativa, S.L. - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{'name': 'Timesheet Activities - Begin/End Hours',
 'version': '10.0.1.0.0',
 'author':  'Camptocamp, '
            'Tecnativa, '
            'Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Human Resources',
 'depends': ['hr_timesheet_sheet',
             ],
 'website': 'http://www.camptocamp.com',
 'data': ['views/hr_analytic_timesheet.xml',
          'views/hr_timesheet_sheet.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
