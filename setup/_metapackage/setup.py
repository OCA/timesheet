import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-hr_timesheet_begin_end>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_name_customer>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_sheet>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_task_domain>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_task_required>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_task_stage>=16.0dev,<16.1dev',
        'odoo-addon-sale_timesheet_line_exclude>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
