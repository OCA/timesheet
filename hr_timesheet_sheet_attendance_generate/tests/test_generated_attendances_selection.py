# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestSheetGeneratedAttendancesSelection(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = cls.env["res.users"]
        cls.employee_model = cls.env["hr.employee"]
        cls.attendance_model = cls.env["hr.attendance"]
        cls.wizard_model = cls.env["hr_timesheet.sheet.generated.attendances.selection"]

        cls.user = cls.user_model.create(
            {
                "name": "Test User",
                "login": "test",
                "password": "test",
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.employee = cls.employee_model.create(
            {
                "name": "TestEmployee",
                "user_id": cls.user.id,
            }
        )

        cls.attendance_1 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 8, 8, 0, 0),
                "check_out": datetime(2024, 4, 8, 17, 0, 0),
            }
        )
        cls.attendance_2 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 12, 9, 0, 0),
                "check_out": datetime(2024, 4, 12, 13, 0, 0),
            }
        )
        cls.attendance_3 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 12, 14, 0, 0),
                "check_out": datetime(2024, 4, 12, 18, 0, 0),
            }
        )
        cls.attendance_4 = cls.attendance_model.create(
            {
                "employee_id": cls.employee.id,
                "check_in": datetime(2024, 4, 13, 10, 0, 0),
                "check_out": datetime(2024, 4, 13, 18, 0, 0),
            }
        )

    def test_generated_attendances_selection(self):
        atts = [
            self.attendance_1.id,
            self.attendance_2.id,
            self.attendance_3.id,
            self.attendance_4.id,
        ]

        ids = {att for att in atts}
        wizard = self.wizard_model.with_context(attendances=atts).create({})
        self.assertEqual(wizard.original_attendance_ids, wizard.attendance_ids)
        self.assertEqual(set(wizard.attendance_ids.ids), ids)
        self.assertEqual(len(wizard.attendance_ids.ids), 4)

        wizard.attendance_ids -= self.attendance_1
        wizard.attendance_ids -= self.attendance_2
        self.assertEqual(len(wizard.attendance_ids.ids), 2)
        self.assertEqual(len(wizard.original_attendance_ids.ids), 4)

        original_count = len(self.env["hr.attendance"].search([]))
        wizard.action_save()
        count = len(self.env["hr.attendance"].search([]))
        self.assertEqual(original_count - 2, count)

        self.assertFalse(self.attendance_1.exists())
        self.assertFalse(self.attendance_2.exists())
        self.assertTrue(self.attendance_3.exists())
        self.assertTrue(self.attendance_4.exists())
