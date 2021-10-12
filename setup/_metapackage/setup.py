import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-crm_timesheet',
        'odoo14-addon-hr_timesheet_activity_begin_end',
        'odoo14-addon-hr_timesheet_analysis',
        'odoo14-addon-hr_timesheet_sheet',
        'odoo14-addon-hr_timesheet_sheet_autodraft',
        'odoo14-addon-hr_timesheet_sheet_policy_project_manager',
        'odoo14-addon-hr_timesheet_task_domain',
        'odoo14-addon-hr_timesheet_task_required',
        'odoo14-addon-hr_timesheet_task_stage',
        'odoo14-addon-hr_timesheet_time_type',
        'odoo14-addon-hr_utilization_analysis',
        'odoo14-addon-sale_timesheet_order_line_sync',
        'odoo14-addon-sale_timesheet_rounded',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
