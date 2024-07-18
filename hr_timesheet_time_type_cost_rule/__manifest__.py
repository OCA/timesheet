# Copyright (C) 2024 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cost Rules in Time Type Timesheet",
    "summary": "Ability to add cost rules based on ratios or fixed price in time type.",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex, Odoo Community Association (OCA)",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["hr_timesheet_time_type"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_time_type_view.xml",
        "views/project_time_type_view_cost_rule.xml",
    ],
    "installable": True,
}
