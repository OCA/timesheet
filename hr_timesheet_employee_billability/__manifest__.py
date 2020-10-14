# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Timesheet Employee Billablity",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """Display a employee timesheet billability report.""",
    "category": "Human Resources",
    "maintainers": ["AmmarOfficewalaSerpentCS"],
    "website": "https://github.com/OCA/timesheet",
    "depends": ["sale_timesheet", "hr_holidays", "hr_holidays_public"],
    "data": [
        "security/ir.model.access.csv",
        "report/timesheet_employee_billablity.xml",
    ],
    'external_dependencies': {
        'python': ['numpy'],
    },
    "qweb": [],
    "auto_install": False,
    "application": False,
    "installable": True,
    "development_status": "Stable",
}
