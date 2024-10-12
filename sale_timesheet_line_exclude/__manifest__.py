# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sales Timesheet: exclude Timesheet Line from Sale Order",
    "version": "17.0.1.1.0",
    "category": "Sales",
    "website": "https://github.com/OCA/timesheet",
    "author": "CorporateHub, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Exclude Timesheet Line from Sale Order",
    "depends": ["sale_timesheet"],
    "data": [
        "security/exclude_from_sale_order.xml",
        "views/account_analytic_line.xml",
        "views/project_task.xml",
    ],
}
