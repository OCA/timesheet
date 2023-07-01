{
    "name": "Timesheet Description Customer",
    "summary": "Add ‘Description Customer’ field for timesheets",
    "version": "16.0.1.0.0",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "maintainers": ["solo4games", "CetmixGitDrone"],
    "author": "Odoo Community Association (OCA), Cetmix",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["hr_timesheet"],
    "data": [
        "views/hr_timesheet_name_customer_views.xml",
        "report/name_customer_template.xml",
    ],
}
