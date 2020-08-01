import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-hr_timesheet_activity_begin_end',
        'odoo13-addon-hr_timesheet_analysis',
        'odoo13-addon-hr_timesheet_sheet',
        'odoo13-addon-hr_timesheet_sheet_autodraft',
        'odoo13-addon-hr_timesheet_sheet_policy_project_manager',
        'odoo13-addon-hr_timesheet_task_domain',
        'odoo13-addon-hr_timesheet_task_required',
        'odoo13-addon-hr_timesheet_task_stage',
        'odoo13-addon-hr_utilization_analysis',
        'odoo13-addon-sale_timesheet_rounded',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
