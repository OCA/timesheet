{
    "name": "Sale Timesheet Costs and Revenues",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "summary": "Pivot report including billed and unbilled timesheet revenue and"
    " cost, by project and period",
    "category": "Sales",
    "author": "Innovara, Odoo Community Association (OCA)",
    "maintainers": ["innovara"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/timesheet",
    "depends": ["project", "hr_timesheet", "sale_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_timesheet_costs_revenues_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
