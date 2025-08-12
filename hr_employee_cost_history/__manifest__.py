# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "HR Employee Cost History",
    "summary": """Adds an history to employee's costs.""",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["SabrinaRMArtin", "rafaelbn"],
    "license": "LGPL-3",
    "external_dependencies": {"python": ["freezegun"]},
    "installable": True,
    "auto_install": False,
    "depends": [
        "hr_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/hr_employee_timesheet_cost_wizard_views.xml",
        "views/hr_employee_timesheet_cost_history_views.xml",
        "views/hr_employee_views.xml",
    ],
}
