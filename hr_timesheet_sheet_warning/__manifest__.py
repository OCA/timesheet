# Copyright 2024 ForgeFlow (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Timesheet Sheet Warning",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "summary": "Timesheet Sheets, Activities",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "installable": True,
    "auto_install": False,
    "depends": ["hr_timesheet_sheet"],
    "data": [
        "security/hr_timesheet_sheet_warning_rules.xml",
        "security/ir.model.access.csv",
        "views/hr_timesheet_sheet_warning_definition.xml",
        "views/hr_timesheet_sheet_warning_item.xml",
        "views/hr_timesheet_sheet.xml",
    ],
}
