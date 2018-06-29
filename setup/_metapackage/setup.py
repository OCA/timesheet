import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-hr-timesheet",
    description="Meta package for oca-hr-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-crm_phonecall_timesheet',
        'odoo10-addon-crm_timesheet',
        'odoo10-addon-hr_employee_product',
        'odoo10-addon-hr_timesheet_activity_begin_end',
        'odoo10-addon-hr_timesheet_no_closed_project_task',
        'odoo10-addon-hr_timesheet_sheet_period',
        'odoo10-addon-hr_timesheet_sheet_week_start_day',
        'odoo10-addon-hr_timesheet_task',
        'odoo10-addon-hr_timesheet_task_required',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
