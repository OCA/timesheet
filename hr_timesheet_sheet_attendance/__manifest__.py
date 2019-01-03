{
    'name': 'HR Timesheet Sheet Attendance',
    'version': '11.0.0.0.0',
    'category': 'Human Resources',
    'sequence': 80,
    'license': 'AGPL-3',
    'depends': [
        'hr_timesheet',
        'hr_attendance',
        'hr_timesheet_sheet'
    ],
    'data': [
        'views/hr_timesheet_sheet_view.xml',
        'views/hr_attendance_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
