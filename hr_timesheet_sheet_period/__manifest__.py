# Copyright 2016-17 ForgeFlow S.L.
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet Sheet based on Payroll Period",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "author": "ForgeFlow S.L., "
    "Serpent Consulting Services Pvt. Ltd., "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "license": "AGPL-3",
    "depends": [
        "hr_period",
        "hr_timesheet_sheet",
    ],
    "data": [
        "views/hr_timesheet_sheet_view.xml",
    ],
    "installable": True,
}
