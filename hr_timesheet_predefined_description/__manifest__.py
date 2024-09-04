# Copyright 2024 Tecnativa - Juan José Seguí
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Timesheet Predefined Description",
    "version": "14.0.1.0.0",
    "category": "Timesheet",
    "summary": "Predefined descriptions for timesheet entries",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "installable": True,
    "auto_install": False,
    "depends": ["hr_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "security/timesheet_predefined_description_security.xml",
        "views/account_analytic_line_views.xml",
        "views/timesheet_predefined_description_views.xml",
    ],
    "demo": [
        "demo/hr_timesheet_predefined_description_demo.xml",
    ],
    "maintainers": ["juanjosesegui-tecnativa"],
}
