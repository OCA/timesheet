# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Timesheet Sheet Prefill",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "summary": "Prefill timesheet sheet lines from the previous period",
    "license": "AGPL-3",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "installable": True,
    "depends": ["hr_timesheet_sheet"],
    "data": [
        "views/hr_timesheet_sheet_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
}
