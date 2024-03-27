import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-crm_timesheet>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_product>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_begin_end>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_sheet>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_sheet_autodraft>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_sheet_begin_end>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_sheet_no_create>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_sheet_period>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_sheet_policy_project_manager>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_task_domain>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_task_required>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_task_stage>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_time_type>=15.0dev,<15.1dev',
        'odoo-addon-sale_timesheet_line_exclude>=15.0dev,<15.1dev',
        'odoo-addon-sale_timesheet_rounded>=15.0dev,<15.1dev',
        'odoo-addon-sale_timesheet_task_exclude>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
