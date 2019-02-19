from odoo.addons.hr_timesheet_sheet_attendance.tests.\
    hr_timesheet_sheet_test_cases import HrTimesheetTestCases
from odoo.exceptions import ValidationError, UserError
from odoo import fields


class TestHrAttendance(HrTimesheetTestCases):

    def setUp(self):
        super(TestHrAttendance, self).setUp()
        checkInDate = '2018-12-12 10:00:00'
        self.attendance_1 = self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string(checkInDate)
        )

    def test_00_compute_sheet_id(self):
        # check sheet_id in attendances
        self.attendance_1._compute_sheet_id()
        self.assertEqual(
            self.timesheet,
            self.attendance_1.sheet_id,
            "Error while computing sheet_id on attendance.\
            \nMethod: _compute_sheet_id"
        )

    def test_01_test_timezone_conversion(self):
        # check for _get_attendance_employee_tz
        self.user_id.tz = 'Etc/GMT+12'
        date = '2018-12-12 10:00:00'
        attDate = self.attendance_1._get_attendance_employee_tz(date=date)
        self.assertEqual(
            attDate, '2018-12-11',
            "Error while converting date/datetime in user's timezone.\
            \nMethod: _get_attendance_employee_tz")

    def test_02_check_timesheet_confirm(self):
        # check check_in & check_out equal or not
        with self.assertRaises(UserError):
            self.timesheet.action_timesheet_confirm()

        # unlink attendance from confirmed timesheet
        self.attendance_1.check_out = '2018-12-12 13:00:00'
        self.timesheet.action_timesheet_confirm()
        with self.assertRaises(UserError):
            self.attendance_1.unlink()

        # create attendance in confirmed timesheet
        with self.assertRaises(ValidationError):
            checkInDate = '2018-12-12 13:35:00'
            self._create_attendance(
                employee=self.employee,
                checkIn=fields.Datetime.from_string(checkInDate)
            )

        # modify attendance in confirmed timesheet
        with self.assertRaises(ValidationError):
            self.attendance_1.write({
                'check_in': '2018-12-12 14:00:00'
            })

    def test_03_check_timesheet(self):
        # check when create attendance out_side the current timesheet date
        with self.assertRaises(ValidationError):
            self.attendance_1.write({
                'check_out': '2018-12-16 17:00:00',
            })
