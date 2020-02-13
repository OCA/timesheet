import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-crm_timesheet',
        'odoo11-addon-hr_timesheet_sheet',
        'odoo11-addon-hr_timesheet_sheet_attendance',
        'odoo11-addon-hr_timesheet_task_required',
        'odoo11-addon-hr_timesheet_task_stage',
        'odoo11-addon-project_task_stage_allow_timesheet',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
