# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale timesheet budget",
    "version": "16.0.1.0.0",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_timesheet"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "views/project_project_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
