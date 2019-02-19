from odoo.addons.hr_timesheet_sheet_attendance.tests.\
    hr_timesheet_sheet_test_cases import HrTimesheetTestCases
from odoo.exceptions import UserError
from odoo import fields


class TestHrTimesheetSheet(HrTimesheetTestCases):

    def test_00_check_timesheet_compute_old_attendance(self):
        """ sheet_id should compute for attendaces which
        have created before creation of timesheet"""
        checkInDate = '2018-11-12 10:00:00'
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string(checkInDate)
        )
        time_sheet = self._create_timesheet_sheet(
            self.employee, '2018-11-12')
        self.assertEqual(
            time_sheet.attendance_count,
            1,
            "Error while computing sheet_id of already created attendances.\
            \nMethod: create"
        )

    def test_01_compute_total_time_and_difference(self):
        """Check for timedifference, total attendance time
        and atteendance count"""

        # Attendance - 1
        checkInDate = '2018-12-12 10:00:00'
        checkOutDate = '2018-12-12 12:00:00'
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string(checkInDate),
            checkOut=fields.Datetime.from_string(checkOutDate)
        )
        self.assertEqual(
            self.timesheet.attendance_count,
            1,
            "Error while computing total attendance count.\
            \nMethod: _compute_attendance_count"
        )
        self.assertEqual(
            self.timesheet.total_attendance,
            2.0,
            "Error while computing total working time.\
            \nMethod: _compute_attendance_time"
        )
        self.assertEqual(
            self.timesheet.total_difference,
            2.0,
            "Error while computing total total difference.\
            \nMethod: _compute_attendance_time"
        )

        # Attendance - 2
        checkInDate = '2018-12-12 13:00:00'
        checkOutDate = '2018-12-12 14:00:00'
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string(checkInDate),
            checkOut=fields.Datetime.from_string(checkOutDate)
        )
        self.timesheet._compute_attendance_count()
        self.assertEqual(
            self.timesheet.attendance_count,
            2,
            "Error while computing total attendance count.\
            \nMethod: _compute_attendance_count"
        )
        self.assertEqual(
            self.timesheet.total_attendance,
            3.0,
            "Error while computing total working time.\
            \nMethod: _compute_attendance_time"
        )
        self.assertEqual(
            self.timesheet.total_difference,
            3.0,
            "Error while computing total total difference.\
            \nMethod: _compute_attendance_time"
        )

        # Create timesheet lines
        self.timesheet.timesheet_ids = [(0, 0, {
            'employee_id': self.employee.id,
            'date': '2018-12-12',
            'project_id': self.project_id.id,
            'task_id': self.task_1.id,
            'name': 'testing',
            'unit_amount': 1.0,
        })]
        self.assertEqual(
            self.timesheet.total_difference,
            2.0,
            "Error while computing total total difference.\
            \nMethod: _compute_attendance_time"
        )

        # # Attendance - 3
        checkInDate = '2018-12-12 16:00:00'
        attendance_3 = self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string(checkInDate)
        )
        with self.assertRaises(UserError):
            self.timesheet.action_timesheet_confirm()

        attendance_3.check_out = '2018-12-12 17:00:00'
        self.timesheet.action_timesheet_confirm()
        self.assertEqual(
            self.timesheet.state,
            'confirm',
            "Error while confirming timesheet.\
            \nMethod: action_timesheet_confirm"
        )

    def test_03_sighin_sighout(self):
        """test Check In/Check Out button on timesheet-sheet"""
        time_sheet = self._create_timesheet_sheet(self.employee)
        time_sheet.attendance_action_change()
        self.assertNotEqual(
            time_sheet.attendances_ids.filtered(
                lambda att: not att.check_out).ids,
            [],
            "Error while sighin using button on timesheet.\
            \nMethod: attendance_action_change"
        )

        time_sheet.attendance_action_change()
        self.assertEqual(
            time_sheet.attendances_ids.filtered(
                lambda att: not att.check_out).ids,
            [],
            "Error while signout using button on timesheet.\
            \nMethod: attendance_action_change"
        )
