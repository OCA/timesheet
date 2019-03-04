import datetime
from odoo.tests.common import TransactionCase
from odoo import fields


class HrTimesheetTestCases(TransactionCase):

    def setUp(self):
        super(HrTimesheetTestCases, self).setUp()
        self.user_id = self._create_user()
        self.employee = self._create_employee(self.user_id)
        self.timesheet = self._create_timesheet_sheet(
            self.employee, datetime.date(2018, 12, 12))
        self.project_id = self.env.ref('project.project_project_1')
        self.task_1 = self.env.ref('project.project_task_1')

    def _create_user(self):
        """Create and return user"""
        user_vals = {
            'name': 'TestUser',
            'login': 'test',
            'password': 'test',
            'company_id': self.env.ref('base.main_company').id,
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('base.group_partner_manager').id
            ])],
        }
        return self.env['res.users'].create(user_vals)

    def _create_employee(self, user):
        """Create employee
        :param user: record set of res.user
        :param return: recordset of hr.employee"""
        employee_vals = {
            'name': 'TestEmployee',
            'user_id': self.user_id.id,
            'department_id': self.env.ref('hr.dep_rd').id,
            'job_id': self.env.ref('hr.job_developer').id,
            'category_ids': [
                (6, 0, [self.env.ref('hr.employee_category_4').id])
            ],
            'work_location': 'Building 1, Second Floor',
            'work_email': 'test@test.com',
            'work_phone': '+3281813700',
        }
        return self.env['hr.employee'].create(employee_vals)

    def _create_timesheet_sheet(self, employee, date=None):
        """Create employee
        :param employee: record set of hr.employee
        :param str date: date
        :param return: recordset of hr_timesheet.sheet"""
        if not date:
            date = fields.Date.today()
        sheet_vals = {
            'employee_id': employee.id,
            'date_start': date,
            'date_end': date,
        }
        return self.env['hr_timesheet.sheet'].create(sheet_vals)

    def _create_attendance(self, employee, checkIn=None, checkOut=None):
        """Create employee
        :param employee: record set of hr.employee
        :param str checkIn: datetime
        :param str checkOut: datetime
        :param return: recordset of hr.attendance"""
        attendance_vals = {
            'employee_id': employee.id,
            'check_in': checkIn,
        }
        if checkOut:
            attendance_vals.update({'check_out': checkOut})
        return self.env['hr.attendance'].create(attendance_vals)
