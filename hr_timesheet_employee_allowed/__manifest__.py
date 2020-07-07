# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Timesheet Employees Allowed",
    "summary": "Limits the Employees that are allowed to enter \
    timesheets for others employees.",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["hr_timesheet"],
    "data": [
        "views/hr_employee_view.xml",
        "views/hr_timesheet_view.xml",
    ],
    "installable": True,
}
