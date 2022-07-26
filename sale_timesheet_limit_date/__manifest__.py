# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice Sales Timesheets with a Date Limit",
    "summary": "Layouts",
    "version": "15.0.1.0.1",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": [
        "sale_timesheet",
        "sale_stock",
    ],
    "website": "https://github.com/OCA/timesheet",
    "data": ["views/sale_order_view.xml", "views/move_form_view.xml"],
    "installable": True,
}
