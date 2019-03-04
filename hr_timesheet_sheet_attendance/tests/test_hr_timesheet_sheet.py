import datetime

from odoo.addons.hr_timesheet_sheet_attendance.tests.\
    hr_timesheet_sheet_test_cases import HrTimesheetTestCases
from odoo.exceptions import UserError


class TestHrTimesheetSheet(HrTimesheetTestCases):

    def test_00_check_timesheet_compute_old_attendance(self):
        """ sheet_id should compute for attendaces which
        were created before creation of timesheet"""
        checkInDate = datetime.datetime(2018, 11, 12, 10, 0, 0)
        self._create_attendance(
            employee=self.employee,
            checkIn=checkInDate,
        )
        time_sheet = self._create_timesheet_sheet(
            self.employee, datetime.date(2018, 11, 12))
        self.assertEqual(
            time_sheet.attendance_count,
            1,
            "Error while computing sheet_id of already created attendances.\
            \nMethod: create"
        )

    def test_01_compute_total_time_and_difference(self):
        """Check for time difference, total attendance time
        and attendance count"""

        # Attendance - 1
        checkInDate = datetime.datetime(2018, 12, 12, 10, 0, 0)
        checkOutDate = datetime.datetime(2018, 12, 12, 12, 0, 0)
        self._create_attendance(
            employee=self.employee,
            checkIn=checkInDate,
            checkOut=checkOutDate,
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
        checkInDate = datetime.datetime(2018, 12, 12, 13, 0, 0)
        checkOutDate = datetime.datetime(2018, 12, 12, 14, 0, 0)
        self._create_attendance(
            employee=self.employee,
            checkIn=checkInDate,
            checkOut=checkOutDate,
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
            'date': datetime.date(2018, 12, 12),
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
        checkInDate = datetime.datetime(2018, 12, 12, 16, 0, 0)
        attendance_3 = self._create_attendance(
            employee=self.employee,
            checkIn=checkInDate,
        )
        with self.assertRaises(UserError):
            self.timesheet.action_timesheet_confirm()

        attendance_3.check_out = datetime.datetime(2018, 12, 12, 17, 0, 0)
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
