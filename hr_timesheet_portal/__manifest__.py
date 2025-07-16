{
    "name": "Timesheet portal (editable)",
    "summary": "Fill in timesheets via the portal",
    "version": "18.0.1.0.0",
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
        "templates/portal.xml",
        "security/hr_timesheet_portal_security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/hr_timesheet_portal.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "hr_timesheet_portal/static/src/**/*",
        ],
    },
}
