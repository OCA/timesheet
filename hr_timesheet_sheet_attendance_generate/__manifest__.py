# Copyright 2024 ForgeFlow (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Timesheet Sheet Attendance Generate",
    "version": "16.0.1.0.0",
    "category": "Human Resources",
    "sequence": 80,
    "summary": "Timesheet Sheets, Activities",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "installable": True,
    "auto_install": False,
    "depends": ["hr_timesheet_sheet_attendance"],
    "data": [
        "wizards/generated_attendances_selection_views.xml",
        "views/hr_timesheet_sheet_views.xml",
        "security/ir.model.access.csv",
    ],
}
