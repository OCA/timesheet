# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR period create timesheet",
    "version": "15.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "category": "Human Resources",
    "depends": ["hr_timesheet_sheet_period"],
    "summary": "This module prepare the timesheets for all the periods selected"
    " for all employees",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "wizards/hr_period_create_timesheet_view.xml",
    ],
    "installable": True,
}
