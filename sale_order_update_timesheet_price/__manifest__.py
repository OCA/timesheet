# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Update Timesheet Price",
    "summary": """Update the unit price of already invoiced sale order lines
    by creating a new line""",
    "version": "19.0.1.0.0",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "license": "AGPL-3",
    "depends": [
        # Odoo Community
        "sale_project",
        "sale_timesheet",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/sale_order_unit_price_update.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
