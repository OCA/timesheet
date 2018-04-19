import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-hr-timesheet",
    description="Meta package for oca-hr-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-hr_timesheet_sheet_restrict_analytic',
        'odoo9-addon-hr_timesheet_sheet_week_start_day',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
