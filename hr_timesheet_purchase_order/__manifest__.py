# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Timesheet Purchase Order",
    "version": "14.0.1.1.0",
    "summary": "HR Timesheet Purchase Order",
    "author": "Ooops, Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "depends": [
        "hr_timesheet_sheet",
        "purchase",
    ],
    "maintainers": ["dessanhemrayev", "aleuffre", "renda-dev"],
    "external_dependencies": {},
    "demo": [],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_actions_server.xml",
        "data/hr_timesheet_cron.xml",
        "views/hr_employee_view.xml",
        "views/res_partner_view.xml",
        "views/hr_timesheet_sheet_view.xml",
        "views/purchase_order_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "qweb": [],
    "installable": True,
    "application": False,
}
