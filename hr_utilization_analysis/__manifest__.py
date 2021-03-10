# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Task Logs Utilization Analysis",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "maintainers": ["alexey-pelykh"],
    "website": "https://github.com/OCA/timesheet",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "View Utilization Analysis from Task Logs.",
    "depends": ["hr_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_department.xml",
        "views/hr_employee.xml",
        "report/hr_utilization_analysis.xml",
        "wizards/hr_utilization_analysis_wizard.xml",
    ],
}
