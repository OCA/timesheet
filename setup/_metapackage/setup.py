import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-hr_timesheet_sheet>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_task_domain>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_task_required>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_activity_begin_end',
        'odoo-addon-hr_timesheet_begin_end',
        'odoo-addon-hr_timesheet_sheet_begin_end',
        'odoo-addon-hr_timesheet_task_stage>=15.0dev,<15.1dev',
        'odoo-addon-hr_timesheet_time_type>=15.0dev,<15.1dev',
        'odoo-addon-sale_timesheet_line_exclude>=15.0dev,<15.1dev',
        'odoo-addon-sale_timesheet_task_exclude>=15.0dev,<15.1dev',
        'odoo14-addon-hr_timesheet_analysis',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
