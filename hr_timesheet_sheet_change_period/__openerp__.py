# -*- coding: utf-8 -*-
# © ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet Change Period",
    "version": "9.0.1.0.0",
    "summary": """
Allows to change covered period while the timesheet is in the draft state""",
    "author": "ACSONE SA/NV, "
              "Odoo Community Association (OCA), "
              "OpenSynergy Indonesia",
    "website": "http://www.acsone.eu",
    "category": "Human Resources",
    "depends": ["hr_timesheet_sheet"],
    "data": [
        "wizard/hr_timesheet_sheet_change_period.xml",
        "views/hr_timesheet_sheet_view.xml",
    ],
    'demo': [
        'demo/hr_timesheet_sheet_change_period_demo.xml',
    ],
    "installable": True,
    "license": "AGPL-3",
}
