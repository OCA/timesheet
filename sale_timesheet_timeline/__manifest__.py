# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Dates planning in sales order lines",
    "version": "16.0.1.0.0",
    "category": "Services/Project",
    "website": "https://github.com/OCA/timesheet",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["sale_timesheet", "project_timeline"],
    "data": ["views/sale_order_views.xml", "views/sale_portal_templates.xml"],
}
