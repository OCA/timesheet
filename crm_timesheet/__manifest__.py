# Copyright 2015 Antiun - Antonio Espinosa
# Copyright 2015 Antiun - Javier Iniesta
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2019 Tecnativa - Jairo Llopis
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "CRM Timesheet",
    "category": "Customer Relationship Management",
    "version": "16.0.1.0.0",
    "depends": ["crm", "project_timesheet_time_control"],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_lead_view.xml",
        "views/hr_timesheet_view.xml",
    ],
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "license": "AGPL-3",
    "installable": True,
}
