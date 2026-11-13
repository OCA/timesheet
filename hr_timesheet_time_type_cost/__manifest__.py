# Copyright 2026 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Timesheet Time Type Cost",
    "summary": "Let a time type drive the analytic cost of timesheet lines",
    "version": "18.0.1.0.0",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "author": "Binhex, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["hr_timesheet_time_type"],
    "data": [
        "views/project_time_type_views.xml",
    ],
}
