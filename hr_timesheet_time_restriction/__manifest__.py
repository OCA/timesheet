# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Time Restriction",
    "version": "12.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/timesheet",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Time Restriction",
    "depends": ["hr_timesheet"],
    "data": [
        "security/res_groups.xml",
        "views/project_project_view.xml",
        "views/res_config_settings_view.xml",
    ],
}
