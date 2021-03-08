# Copyright 2016-2017 ACSONE SA/NV
# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hr Timesheet Task Required",
    "summary": """
        Set task on timesheet as a mandatory field""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, CorporateHub, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["hr_timesheet"],
    "data": [
        "views/account_analytic_line.xml",
        "views/project_project.xml",
        "views/res_config_settings.xml",
    ],
}
