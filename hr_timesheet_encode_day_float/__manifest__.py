# Copyright 2026 Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Timesheet Encode Day Float",
    "version": "18.0.1.0.0",
    "summary": "Encode timesheets in days with free decimal input",
    "category": "Services/Timesheets",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/timesheet",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "development_status": "Alpha",
    "maintainers": ["marcelsavegnago"],
    "depends": ["hr_timesheet"],
    "data": [
        "data/uom_data.xml",
    ],
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
