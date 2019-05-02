# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sales Timesheet: Employee/Role",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/timesheet",
    "author":
        "CorporateHub, "
        "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Employee/Role-based rates and billing",
    "depends": [
        "sale_timesheet_hook",
        "sale_timesheet_line_exclude",
        "hr_timesheet_role",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_project.xml",
        "views/project_task.xml",
        "wizard/project_create_sale_order.xml",
    ],
}
