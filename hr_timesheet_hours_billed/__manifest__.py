{
    "name": "Timesheet Hours Billed",
    "summary": """Add ‘Hours Billed’, 'Approved', 'Approved by',
    'Approved on' field for timesheets""",
    "version": "16.0.1.0.0",
    "category": "Timesheet",
    "website": "https://github.com/OCA/timesheet",
    "maintainers": ["solo4games", "CetmixGitDrone"],
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["hr_timesheet", "sale_management"],
    "data": [
        "views/account_analytic_line_view.xml",
    ],
}
