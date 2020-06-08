# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Time Type in Timesheet",
    "summary": "Ability to add time type in timesheet lines.",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["hr_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_time_type_view.xml",
        "views/account_analytic_line_view.xml",
    ],
    "installable": True,
}
