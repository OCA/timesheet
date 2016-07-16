# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2016 OpenSynergy Indonesia (<https://opensynergy-indonesia.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from datetime import datetime, timedelta
from openerp.tools import float_compare


class TestHrAttendance(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestHrAttendance, self).setUp(*args, **kwargs)
        self.obj_contract = self.env["hr.contract"]
        self.obj_attendance = self.env["hr.attendance"]
        self.employee = self.env.ref("hr.employee")
        self.working_hours = self.env.ref("resource.timesheet_group1")
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=365)
        days_ahead = -1 * self.start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        self.next_monday = self.start_date + timedelta(days_ahead)

        self.contract_data = {
            "name": "Contract for administrator",
            "employee_id": self.employee.id,
            "working_hours": self.working_hours.id,
            "date_start": self.start_date.strftime("%Y-%m-%d"),
            "wage": 1500.00,
            "date_end": self.end_date.strftime("%Y-%m-%d"),
        }
        self.contract = self.obj_contract.create(self.contract_data)

        return result

    def test_no_rounding_1(self):

        attn_si = self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_in",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 08:00:00",
        })

        self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_out",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 18:00:00",
        })

        self.env.user.company_id.update_attendance_data()

        self.assertEqual(
            float_compare(
                attn_si.duration,
                10.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.inside_calendar_duration,
                9.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.outside_calendar_duration,
                1.0,
                precision_rounding=0.0000001,
            ),
            0)

    def test_no_rounding_2(self):

        attn_si = self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_in",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 07:30:00",
        })

        self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_out",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 18:30:00",
        })

        self.env.user.company_id.update_attendance_data()

        self.assertEqual(
            float_compare(
                attn_si.duration,
                11.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.inside_calendar_duration,
                9.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.outside_calendar_duration,
                2.0,
                precision_rounding=0.0000001,
            ),
            0)

    def test_no_rounding_3(self):

        attn_si = self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_in",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 08:30:00",
        })

        self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_out",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 11:30:00",
        })

        self.env.user.company_id.update_attendance_data()

        self.assertEqual(
            float_compare(
                attn_si.duration,
                3.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.inside_calendar_duration,
                3.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.outside_calendar_duration,
                0.0,
                precision_rounding=0.0000001,
            ),
            0)

    def test_attendance_rounding_1(self):
        self.working_hours.update({"attendance_rounding": "2"})

        attn_si = self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_in",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 08:40:00",
        })

        self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_out",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 12:00:00",
        })

        self.env.user.company_id.update_attendance_data()

        self.assertEqual(
            float_compare(
                attn_si.duration,
                3.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.inside_calendar_duration,
                3.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.outside_calendar_duration,
                0.0,
                precision_rounding=0.0000001,
            ),
            0)

    def test_overtime_rounding_1(self):
        self.working_hours.update({"overtime_rounding": "2"})

        attn_si = self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_in",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 08:00:00",
        })

        self.obj_attendance.create({
            "employee_id": self.employee.id,
            "action": "sign_out",
            "name": self.next_monday.strftime("%Y-%m-%d") + " 12:40:00",
        })

        self.env.user.company_id.update_attendance_data()

        self.assertEqual(
            float_compare(
                attn_si.duration,
                4.666666667,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.inside_calendar_duration,
                4.0,
                precision_rounding=0.0000001,
            ),
            0)

        self.assertEqual(
            float_compare(
                attn_si.outside_calendar_duration,
                0.5,
                precision_rounding=0.0000001,
            ),
            0)
