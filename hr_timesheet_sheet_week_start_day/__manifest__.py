# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
#     (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Hr Timesheet Sheet Week Start Day",
    "summary": "Allows to define the week start date for Timesheets at "
               "company level",
    "version": "10.0.1.0.0",
    "author": "Eficent Business and IT Consulting Services, S.L., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Generic",
    "depends": ["hr_timesheet_sheet", "project"],
    "license": "AGPL-3",
    "data": [
        "views/project_config_settings_view.xml",
    ],
    'installable': True,
}
