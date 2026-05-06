# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
{
    "name": "HR Timesheet Amount Security",
    "summary": "Add security restrictions to timesheet amount fields",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Human Resources/Timesheets",
    "website": "https://github.com/OCA/timesheet",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual", "rafaelbn"],
    "license": "LGPL-3",
    "depends": [
        "analytic_amount_security",
        "hr_timesheet",
        "hr_timesheet_attendance",
    ],
    "data": [],
    "auto_install": False,
    "installable": True,
}
