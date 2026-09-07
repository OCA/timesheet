import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class HrTimesheetTestCases(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_id = cls._create_user()
        cls.employee = cls._create_employee(cls.user_id)
        cls.timesheet = cls._create_timesheet_sheet(
            cls.employee, datetime.date(2018, 12, 12)
        )
        cls.project_id = cls.env["project.project"].create({"name": "Test Project"})
        cls.task_1 = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project_id.id,
            }
        )

    @classmethod
    def _create_user(cls):
        """Create and return user"""
        user_vals = {
            "name": "TestUser",
            "login": "test",
            "password": "test",
            "company_id": cls.env.company.id,
            "group_ids": [
                (6, 0, [cls.env.ref("base.group_user").id]),
            ],
        }
        return cls.env["res.users"].create(user_vals)

    @classmethod
    def _create_employee(cls, user):
        """Create employee"""
        department = cls.env["hr.department"].create({"name": "Test Dept"})
        job = cls.env["hr.job"].create({"name": "Test Job"})
        employee_vals = {
            "name": "TestEmployee",
            "user_id": cls.user_id.id,
            "department_id": department.id,
            "job_id": job.id,
            "work_email": "test@test.com",
            "work_phone": "+3281813700",
        }
        return cls.env["hr.employee"].create(employee_vals)

    @classmethod
    def _create_timesheet_sheet(cls, employee, date=None):
        """Create employee
        :param employee: record set of hr.employee
        :param str date: date
        :param return: recordset of hr_timesheet.sheet"""
        if not date:
            date = fields.Date.today()
        sheet_vals = {
            "employee_id": employee.id,
            "date_start": date,
            "date_end": date,
        }
        return cls.env["hr_timesheet.sheet"].create(sheet_vals)

    @classmethod
    def _create_attendance(cls, employee, checkIn=None, checkOut=None):
        """Create employee
        :param employee: record set of hr.employee
        :param str checkIn: datetime
        :param str checkOut: datetime
        :param return: recordset of hr.attendance"""
        attendance_vals = {
            "employee_id": employee.id,
            "check_in": checkIn,
        }
        if checkOut:
            attendance_vals.update({"check_out": checkOut})
        return cls.env["hr.attendance"].create(attendance_vals)
