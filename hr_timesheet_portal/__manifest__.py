# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Timesheet portal (editable)",
    "summary": "Fill in timesheets via the portal",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Website",
    "website": "https://github.com/OCA/timesheet",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet",
        "portal",
        "website",
    ],
    "data": [
        "templates/assets.xml",
        "templates/portal.xml",
        "security/hr_timesheet_portal_security.xml",
        "security/ir.model.access.csv",
        "views/hr_employee.xml",
    ],
    "demo": [
        "demo/hr_timesheet_portal.xml",
    ],
}
