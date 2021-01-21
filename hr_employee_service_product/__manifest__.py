# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Service Products on Employee Timesheet",
    "summary": "Assign a service product to employees.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["product", "hr_timesheet", "account"],
    "data": [
        "views/hr_employee_views.xml",
    ],
    "installable": True,
    "maintainer": "dreispt",
    "development_status": "Beta",
}
