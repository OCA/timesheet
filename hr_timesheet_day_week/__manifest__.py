# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Timesheets - Day of Week",
    "category": "Human Resources",
    "version": "18.0.1.0.0",
    "depends": ["hr_timesheet"],
    "data": ["views/hr_timesheet_view.xml", "report/timesheets_analysis_report.xml"],
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/timesheet",
    "license": "AGPL-3",
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
