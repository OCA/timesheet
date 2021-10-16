import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-crm_timesheet',
        'odoo8-addon-crm_timesheet_analytic_partner',
        'odoo8-addon-hr_employee_product',
        'odoo8-addon-hr_timesheet_activity_begin_end',
        'odoo8-addon-hr_timesheet_holiday',
        'odoo8-addon-hr_timesheet_improvement',
        'odoo8-addon-hr_timesheet_invoice_hide_to_invoice',
        'odoo8-addon-hr_timesheet_invoice_hide_to_invoice_task',
        'odoo8-addon-hr_timesheet_no_closed_project_task',
        'odoo8-addon-hr_timesheet_print_employee_timesheet',
        'odoo8-addon-hr_timesheet_sheet_change_period',
        'odoo8-addon-hr_timesheet_task',
        'odoo8-addon-hr_timesheet_task_required',
        'odoo8-addon-timesheet_task',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
