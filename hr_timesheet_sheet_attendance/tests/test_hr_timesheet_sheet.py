import datetime

from odoo.exceptions import UserError

from .hr_timesheet_sheet_test_cases import HrTimesheetTestCases


class TestHrTimesheetSheet(HrTimesheetTestCases):
    def test_00_check_timesheet_compute_old_attendance(self):
        """sheet_id should compute for attendaces which
        were created before creation of timesheet"""
        checkInDate = datetime.datetime(2018, 11, 12, 10, 0, 0)
        self._create_attendance(
            employee=self.employee,
            checkIn=checkInDate,
        )
        time_sheet = self._create_timesheet_sheet(
            self.employee, datetime.date(2018, 11, 12)
        )
        self.assertEqual(
            time_sheet.attendance_count,
            1,
            "Error while computing sheet_id of already created attendances.\
            \nMethod: create",
        )

    def test_01_compute_total_time_and_difference(self):
        """Check for time difference, total attendance time
        and attendance count"""

        # Attendance - 1
        checkInDate = datetime.datetime(2018, 12, 12, 9, 0, 0)
        checkOutDate = datetime.datetime(2018, 12, 12, 11, 0, 0)
        self._create_attendance(
            employee=self.employee,
            checkIn=checkInDate,
            checkOut=checkOutDate,
        )
        self.assertEqual(
            self.timesheet.attendance_count,
            1,
            "Error while computing total attendance count.\
            \nMethod: _compute_attendance_count",
        )
        self.assertEqual(
            self.timesheet.total_attendance,
            2.0,
            "Error while computing total working time.\
            \nMethod: _compute_attendance_time",
        )
        self.assertEqual(
            self.timesheet.total_difference,
            2.0,
            "Error while computing total total difference.\
            \nMethod: _compute_attendance_time",
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
            \nMethod: _compute_attendance_count",
        )
        self.assertEqual(
            self.timesheet.total_attendance,
            3.0,
            "Error while computing total working time.\
            \nMethod: _compute_attendance_time",
        )
        self.assertEqual(
            self.timesheet.total_difference,
            3.0,
            "Error while computing total total difference.\
            \nMethod: _compute_attendance_time",
        )

        # Create timesheet lines
        self.timesheet.timesheet_ids = [
            (
                0,
                0,
                {
                    "employee_id": self.employee.id,
                    "date": datetime.date(2018, 12, 12),
                    "project_id": self.project_id.id,
                    "task_id": self.task_1.id,
                    "name": "testing",
                    "unit_amount": 1.0,
                },
            )
        ]
        self.assertEqual(
            self.timesheet.total_difference,
            2.0,
            "Error while computing total total difference.\
            \nMethod: _compute_attendance_time",
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
            "confirm",
            "Error while confirming timesheet.\
            \nMethod: action_timesheet_confirm",
        )

    def test_03_sighin_sighout(self):
        """test Check In/Check Out button on timesheet-sheet"""
        time_sheet = self._create_timesheet_sheet(self.employee)
        time_sheet.attendance_action_change()
        self.assertNotEqual(
            time_sheet.attendances_ids.filtered(lambda att: not att.check_out).ids,
            [],
            "Error while sighin using button on timesheet.\
            \nMethod: attendance_action_change",
        )

        time_sheet.attendance_action_change()
        self.assertEqual(
            time_sheet.attendances_ids.filtered(lambda att: not att.check_out).ids,
            [],
            "Error while signout using button on timesheet.\
            \nMethod: attendance_action_change",
        )

    def test_04_create_timezone_boundary_next_day(self):
        """Test attendance at UTC date boundary that's next day in employee timezone.
        Employee timezone is Europe/Brussels (UTC+1 in winter, UTC+2 in summer).
        """
        # Set employee timezone to Europe/Brussels for timezone boundary tests
        self.user_id.tz = "Europe/Brussels"
        # Attendance at Jan 14, 23:30 UTC = Jan 15, 00:30 Brussels (UTC+1)
        # So it's Jan 15 in employee's timezone
        attendance = self._create_attendance(
            employee=self.employee,
            checkIn=datetime.datetime(2019, 1, 14, 23, 30, 0),
            checkOut=datetime.datetime(2019, 1, 15, 2, 0, 0),
        )
        # Timesheet for Jan 15-20
        timesheet = self._create_timesheet_sheet(
            self.employee, datetime.date(2019, 1, 15)
        )
        # Should be included (check_in is Jan 15 in Brussels)
        self.assertIn(
            attendance.id,
            timesheet.attendances_ids.ids,
            "Attendance should be included (Jan 14 23:30 UTC = Jan 15 in Brussels).\
            \nMethod: create",
        )
