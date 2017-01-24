# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "HR Timesheet Sheet based on Payroll Period",
    'version': '9.0.1.0.0',
    'category': 'Human Resources',
    "author": "Eficent,"
              "SerpentCS,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.eficent.com',
    'license': 'AGPL-3',
    "depends": ['hr_period', 'hr_timesheet_sheet'],
    "data": [
        'views/hr_timesheet_sheet_view.xml',
    ],
    "installable": True
}
