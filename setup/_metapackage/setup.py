import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-crm_timesheet',
        'odoo14-addon-hr_employee_product',
        'odoo14-addon-hr_timesheet_activity_begin_end',
        'odoo14-addon-hr_timesheet_analysis',
        'odoo14-addon-hr_timesheet_employee_analytic_tag',
        'odoo14-addon-hr_timesheet_predefined_description',
        'odoo14-addon-hr_timesheet_purchase_order',
        'odoo14-addon-hr_timesheet_report',
        'odoo14-addon-hr_timesheet_report_milestone',
        'odoo14-addon-hr_timesheet_sheet',
        'odoo14-addon-hr_timesheet_sheet_activity',
        'odoo14-addon-hr_timesheet_sheet_attendance',
        'odoo14-addon-hr_timesheet_sheet_autodraft',
        'odoo14-addon-hr_timesheet_sheet_no_create',
        'odoo14-addon-hr_timesheet_sheet_period',
        'odoo14-addon-hr_timesheet_sheet_policy_department_manager',
        'odoo14-addon-hr_timesheet_sheet_policy_project_manager',
        'odoo14-addon-hr_timesheet_task_domain',
        'odoo14-addon-hr_timesheet_task_required',
        'odoo14-addon-hr_timesheet_task_stage',
        'odoo14-addon-hr_timesheet_time_restriction',
        'odoo14-addon-hr_timesheet_time_type',
        'odoo14-addon-hr_utilization_analysis',
        'odoo14-addon-hr_utilization_report',
        'odoo14-addon-project_task_stage_allow_timesheet',
        'odoo14-addon-sale_timesheet_budget',
        'odoo14-addon-sale_timesheet_line_exclude',
        'odoo14-addon-sale_timesheet_order_line_no_update',
        'odoo14-addon-sale_timesheet_order_line_sync',
        'odoo14-addon-sale_timesheet_rounded',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
