# Copyright 2025 Moduon Team SL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Timesheet Manager Approver",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "summary": "Allow timesheet approvers to manage subordinate timesheets",
    "license": "AGPL-3",
    "author": "Moduon, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["hr_timesheet"],
    "maintainers": ["EmilioPascual", "rafaelbn"],
    "data": [
        "security/hr_timesheet_manager_approver_security.xml",
    ],
    "installable": True,
    "auto_install": False,
}
