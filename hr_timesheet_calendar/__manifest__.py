# Copyright 2025 Lansana Barry Sow(APSL-Nagarro)<lbarry@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Timesheet Calendar",
    "version": "16.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "Lansana Barry Sow, APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["lbarry-apsl"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_timesheet",
        "project_timesheet_time_control",
    ],
    "data": [
        "views/hr_timesheet_views.xml",
    ],
}
