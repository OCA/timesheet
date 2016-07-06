# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hr Timesheet Sheet Week Start Day",
    "summary": "Allows to define the week start date for Timesheets at "
               "company level",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services, S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Generic",
    "depends": ["hr_timesheet_sheet"],
    "license": "AGPL-3",
    "data": [
        "views/res_company_view.xml",
    ],
    'installable': True,
}
