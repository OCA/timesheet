# Copyright 2025 S.S.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Timesheet - Begin/End Hours + Break",
    "version": "18.0.1.0.0",
    "author": "S.S., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Services/Timesheet",
    "depends": [
        "hr_timesheet",
        "hr_timesheet_begin_end",
        "project",
    ],
    "website": "https://github.com/OCA/timesheet",
    "data": [
        "views/hr_analytic_timesheet.xml",
        "views/project_task_view.xml",
    ],
    "installable": True,
    "summary": "Adds break duration to begin/end timesheets",
}
