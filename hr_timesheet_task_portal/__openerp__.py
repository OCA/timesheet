# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet Task Portal",
    "summary": "Allows portal users to display the timesheet entries made to "
               "a task",
    "version": "8.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services SL, "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Generic",
    "depends": ["hr_timesheet_task", "portal"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv"
        "security/portal_security.xml"
    ],
    'installable': True,
    'active': False,
}
