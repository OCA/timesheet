# -*- coding: utf-8 -*-
# Copyright 2017 Scopea, Niboo SPRL, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR - Task In Timesheets',
    'category': 'HR',
    'summary': 'Allow the user to select task in a timesheet',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'version': '10.0.1.0.0',
    'author': 'Scopea, Niboo, Camptocamp SA, Odoo Community Association (OCA)',
    'depends': ['hr_timesheet_sheet'],
    'data': [
        'views/hr_timesheet_assets.xml',
        'views/hr_timesheet_view.xml',
    ],
    'qweb': [
        'static/src/xml/timesheet.xml',
    ],
    'installable': True,
    'application': False,
}
