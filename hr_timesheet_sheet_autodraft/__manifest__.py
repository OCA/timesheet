# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet Sheet Auto-draft",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": (
        "Automatically draft a Timesheet Sheet for every time entry that does"
        " not have a relevant Timesheet Sheet existing."
    ),
    "depends": ["hr_timesheet_sheet"],
    "data": ["views/account_analytic_line.xml", "views/res_config_settings.xml"],
}
