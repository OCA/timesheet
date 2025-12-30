# Copyright 2025 Acysos S.L. (https://www.acysos.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Portal Timesheet Input (Weekly Grid)",
    "summary": "Portal Weekly Timesheet Grid Entry",
    "author": "Acysos S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "category": "Operations/Timesheets",
    "version": "18.0.1.0.0",
    "depends": ["portal", "hr_timesheet", "project"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/portal_templates.xml",
        "views/hr_employee_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "portal_timesheet_input/static/src/js/timesheet_input.esm.js",
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
