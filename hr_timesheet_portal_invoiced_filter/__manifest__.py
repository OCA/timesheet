# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Timesheet Portal - Invoiced Filter",
    "version": "19.0.1.0.0",
    "author": "NICO SOLUTIONS - ENGINEERING & IT, Odoo Community Association (OCA)",
    "maintainers": ["NICO-SOLUTIONS"],
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["base", "sale_timesheet"],
    "data": [
        "views/sale_timesheet_portal_templates.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
    ],
    "website": "https://github.com/OCA/timesheet",
    "installable": True,
    "auto_install": False,
}
