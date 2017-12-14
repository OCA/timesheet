# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "HR Timesheet Sheet based on Payroll Period",
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Serpent Consulting Services Pvt. Ltd., "
              "Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['hr_period', 'hr_timesheet_sheet'],
    "data": [
        'views/hr_timesheet_sheet_view.xml',
    ],
    "installable": True
}
