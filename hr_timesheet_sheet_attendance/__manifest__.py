{
    'name': 'HR Timesheet Sheet Attendance',
    'version': '12.0.1.0.1',
    'category': 'Human Resources',
    'sequence': 80,
    'license': 'AGPL-3',
    "author": "BizzAppDev, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr-timesheet/",
    'depends': [
        'hr_attendance',
        'hr_timesheet_sheet'
    ],
    'data': [
        'views/hr_timesheet_sheet_view.xml',
        'views/hr_attendance_view.xml',
    ],
    'installable': True,
}
