# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Sergio Teruel
# Copyright 2016-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Ernesto Tejeda
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Task Log: Open/Close Task",
    "version": "17.0.1.0.0",
    "category": "Operations/Timesheets",
    "website": "https://github.com/OCA/timesheet",
    "author": "Tecnativa, CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Open/Close task from corresponding Task Log entry",
    "depends": ["hr_timesheet"],
    "data": ["views/account_analytic_line.xml"],
}
