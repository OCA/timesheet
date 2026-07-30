# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "HR - Timesheet Cost Account",
    "summary": "Accounting Cost for Timesheet",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "license": "AGPL-3",
    "depends": [
        "analytic",
        "account",
        "hr_hourly_cost",
        "hr_timesheet",
    ],
    "data": [
        "data/sequence.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/hr_timesheet_costing_views.xml",
        "views/account_move_views.xml",
    ],
    "maintainers": ["Saran440"],
}
