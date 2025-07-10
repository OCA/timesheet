# Copyright 2025 Kencove (https://www.kencove.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Timesheet Hide Documents Section",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": """Hide Timesheet document section on customer portal.""",
    "depends": ["hr_timesheet"],
    "author": "Kencove, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "category": "Services/Timesheets",
    "data": ["views/hr_timesheet_portal_templates.xml"],
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
