# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Timesheet Analytic Tags",
    "summary": """
        Use analytic tags from sale order line on analytic lines generated
        from tasks""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["sale_timesheet"],
    "data": [
        "views/project_task.xml",
    ],
    "demo": [],
}
