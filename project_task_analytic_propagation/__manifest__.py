# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/LGPL-3.0)

{
    "name": "Project Task Analytic Propagation",
    "summary": "Updates timesheet's analytic account"
    " when their task changes the analytic.",
    "version": "18.0.1.0.1",
    "development_status": "Alpha",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Andrii9090", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_timesheet",
    ],
    "data": [
        "views/project_task_views.xml",
    ],
}
