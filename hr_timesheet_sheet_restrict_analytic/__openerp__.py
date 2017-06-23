# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. (www.eficent.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Hr Timesheet Sheet Restrict Analytic",
    "summary": "Allows to restrict the analytic accounts that can be "
               "used in timesheets",
    "version": "9.0.1.0.0",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr-timesheet",
    "category": "Human Resources",
    "depends": ["hr_timesheet_sheet"],
    "data": [
        "views/analytic_view.xml",
        "views/hr_timesheet_sheet_view.xml",
        "views/hr_timesheet_restrict_analytic.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
}
