# -*- coding: utf-8 -*-
{
    'name': 'Toggl Connector',
    'version': '8.0.1.0.0',
    'category': 'Connector',
    'depends': [
        'connector',
        'hr_timesheet_sheet',
        'hr_timesheet_invoice',
    ],
    'external_dependencies': {
        'python': [
            'requests'
        ],
    },
    'author': 'Sunflower IT',
    'license': 'AGPL-3',
    'website': 'http://sunflowerweb.nl',
    'data': [
        'security/ir.model.access.csv',
        'views/backend.xml',
        'views/menu.xml',
        'views/hr_timesheet_sheet_view.xml',
    ],
    'installable': True,
    'application': True,
 }
