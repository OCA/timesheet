from odoo.addons.hr_timesheet_sheet_attendance.tests.\
    hr_timesheet_sheet_test_cases import HrTimesheetTestCases
from odoo import fields


class TestAttendanceByDay(HrTimesheetTestCases):

    def setUp(self):
        super(TestAttendanceByDay, self).setUp()

        sheet_vals = {
            'employee_id': self.employee.id,
            'date_start': '2019-04-01',
            'date_end': '2019-04-05',
        }
        self.timesheet = self.env['hr_timesheet.sheet'].create(sheet_vals)

    def test_attendance_single_day(self):
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-01 10:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-01 15:00:00')
        )
        res = self.timesheet.get_attendance_by_day()
        self.assertEqual(res, [5.0, 0.0, 0.0, 0.0, 0.0])

    def test_attendance_gap_day(self):
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-01 10:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-01 15:00:00')
        )
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-03 10:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-03 15:00:00')
        )
        res = self.timesheet.get_attendance_by_day()
        self.assertEqual(res, [5.0, 0.0, 5.0, 0.0, 0.0])

    def test_accross_midnight(self):
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-01 19:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-02 05:00:00')
        )
        res = self.timesheet.get_attendance_by_day()
        self.assertEqual(res, [5.0, 5.0, 0.0, 0.0, 0.0])

    def test_spanning_multiple_days(self):
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-01 19:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-03 05:00:00')
        )
        res = self.timesheet.get_attendance_by_day()
        self.assertEqual(res, [5.0, 24.0, 5.0, 0.0, 0.0])

    def test_accross_midnight_with_gap(self):
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-01 19:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-02 05:00:00')
        )
        self._create_attendance(
            employee=self.employee,
            checkIn=fields.Datetime.from_string('2019-04-02 19:00:00'),
            checkOut=fields.Datetime.from_string('2019-04-03 05:00:00')
        )
        res = self.timesheet.get_attendance_by_day()
        # Default Odoo code counts overlaping attendencies hours on the first
        # day of the attendency.
        self.assertEqual(res, [10.0, 10.0, 0.0, 0.0, 0.0])
