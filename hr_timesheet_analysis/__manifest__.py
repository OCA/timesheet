# Copyright 2018-2020 Brainbean Apps
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Task Logs Analysis",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "maintainers": ["alexey-pelykh"],
    "website": "https://github.com/OCA/timesheet",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Analyze tracked time in Graph views",
    "depends": ["hr_timesheet"],
    "data": ["views/account_analytic_line.xml"],
}
