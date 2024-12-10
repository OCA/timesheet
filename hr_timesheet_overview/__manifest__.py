# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet Overview",
    "version": "15.0.1.3.0",
    "license": "AGPL-3",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "depends": [
        "board",
        "hr",
        "hr_contract",
        "hr_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "views/hr_employee_hour_views.xml",
        "wizards/hr_employee_hour_updater_view.xml",
        "report/hr_employee_hour_report_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
