# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

from datetime import datetime, date, time


class TestProjectTimesheetHolidaysRecalculate(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.wednesday = date(2018, 2, 6)
        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.LeaveType = self.env['hr.leave.type']
        self.SudoLeaveType = self.LeaveType.sudo()
        self.LeaveAllocation = self.env['hr.leave.allocation']
        self.SudoLeaveAllocation = self.LeaveAllocation.sudo()
        self.Leave = self.env['hr.leave']
        self.SudoLeave = self.Leave.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
        })
        leave_type = self.SudoLeaveType.create({
            'name': 'Leave Type #1',
            'allocation_type': 'fixed',
            'holiday_type': 'employee',
        })

        self.assertTrue(leave_type.timesheet_generate)
        self.assertTrue(leave_type.timesheet_project_id)
        self.assertTrue(leave_type.timesheet_task_id)

        allocation = self.SudoLeaveAllocation.create({
            'name': 'Allocation #1',
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 1,
        })
        allocation.action_approve()

        leave = self.SudoLeave.create({
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

        leave.timesheet_ids.unit_amount = 4
        leave.timesheet_ids.action_recalculate_timesheet_from_leave()
        self.assertEqual(leave.timesheet_ids.unit_amount, 8)
