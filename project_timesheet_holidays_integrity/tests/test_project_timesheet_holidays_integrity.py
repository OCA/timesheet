# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import UserError

from datetime import datetime, date, time


class TestProjectTimesheetHolidaysIntegrity(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.wednesday = date(2018, 2, 6)
        self.Employee = self.env['hr.employee']
        self.LeaveType = self.env['hr.leave.type']
        self.LeaveAllocation = self.env['hr.leave.allocation']
        self.Leave = self.env['hr.leave']
        self.AccountAnalyticLine = self.env['account.analytic.line']

    def test_1(self):
        employee = self.Employee.create({
            'name': 'Employee',
        })
        leave_type = self.LeaveType.create({
            'name': 'Leave Type',
            'allocation_type': 'fixed',
            'holiday_type': 'employee',
            'validity_start': self.wednesday,
        })

        self.assertTrue(leave_type.timesheet_generate)
        self.assertTrue(leave_type.timesheet_project_id)
        self.assertTrue(leave_type.timesheet_task_id)

        allocation = self.LeaveAllocation.create({
            'name': 'Allocation',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 1,
        })
        allocation.action_approve()

        leave = self.Leave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'date_from': datetime.combine(self.wednesday, time.min),
            'date_to': datetime.combine(self.wednesday, time.max),
        })
        leave._onchange_leave_dates()
        self.assertEqual(leave.number_of_days, 1)
        leave.action_validate()

        self.assertEqual(len(leave.timesheet_ids), 1)
        self.assertEqual(leave.timesheet_ids.unit_amount, 8)

        leave.timesheet_ids.with_context(
            skip_leave_integrity_check=True,
        ).unit_amount = 4
        leave.timesheet_ids.action_restore_data_integrity_with_leaves()
        self.assertEqual(leave.timesheet_ids.unit_amount, 8)

        leave.timesheet_ids.with_context(
            skip_leave_integrity_check=True,
        ).unit_amount = 4
        leave.action_restore_data_integrity_with_timesheets()
        self.assertEqual(leave.timesheet_ids.unit_amount, 8)

    def test_2(self):
        employee = self.Employee.create({
            'name': 'Employee',
        })
        leave_type = self.LeaveType.create({
            'name': 'Leave Type',
            'allocation_type': 'fixed',
            'holiday_type': 'employee',
            'validity_start': self.wednesday,
        })

        self.assertTrue(leave_type.timesheet_generate)
        self.assertTrue(leave_type.timesheet_project_id)
        self.assertTrue(leave_type.timesheet_task_id)

        allocation = self.LeaveAllocation.create({
            'name': 'Allocation',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 1,
        })
        allocation.action_approve()

        leave = self.Leave.create({
            'holiday_status_id': leave_type.id,
            'holiday_type': 'employee',
            'employee_id': employee.id,
            'date_from': datetime.combine(self.wednesday, time.min),
            'date_to': datetime.combine(self.wednesday, time.max),
        })
        leave._onchange_leave_dates()
        self.assertEqual(leave.number_of_days, 1)
        leave.action_validate()

        self.assertEqual(len(leave.timesheet_ids), 1)
        self.assertEqual(leave.timesheet_ids[0].unit_amount, 8)

        with self.assertRaises(UserError):
            leave.timesheet_ids[0].unit_amount = 4
