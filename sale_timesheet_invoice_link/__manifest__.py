# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Sale Timesheet Invoice Link",
    "summary": "Link invoices with timesheet lines",
    "version": "18.0.1.0.1",
    "development_status": "Alpha",
    "category": "Services/Timesheets",
    "website": "https://github.com/OCA/timesheet",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["rafaelbn", "yajo"],
    "license": "LGPL-3",
    "depends": ["sale_timesheet"],
    "data": [
        "views/account_analytic_line_view.xml",
    ],
}
