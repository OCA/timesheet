# Copyright 2022 Dinar Gabbasov
# Copyright 2022 Ooops404
# Copyright 2022 Cetmix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Timesheet Sheet Restriction",
    "version": "14.0.1.0.1",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Restrictions on the creation of time sheets for past dates",
    "depends": ["hr_timesheet"],
    "data": [
        "security/res_groups.xml",
        "views/project_project_view.xml",
        "views/res_config_settings_view.xml",
    ],
}
