# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Timesheet Portal Project Visibility",
    "summary": "Choose per project whether the portal shows its timesheets",
    "version": "18.0.1.0.0",
    "category": "Services/Timesheets",
    "website": "https://github.com/OCA/timesheet",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["hr_timesheet"],
    "data": [
        "security/account_analytic_line_security.xml",
        "views/project_project_views.xml",
        "views/project_task_portal_templates.xml",
        "views/project_task_sharing_views.xml",
    ],
}
