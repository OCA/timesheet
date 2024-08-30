from odoo.addons.hr_timesheet_sheet.tests import test_hr_timesheet_sheet


def sheet_vals(self, date, task, sheet):
    return {
        "name": "/",
        "employee_id": self.employee.id,
        "sheet_id": sheet.id,
        "unit_amount": 1,
        "date": date,
        "task_id": task.id,
        "project_id": task.project_id.id,
    }


def create_sheet(self, start, end):
    return self.env["hr_timesheet.sheet"].create(
        {
            "company_id": self.employee.company_id.id,
            "employee_id": self.employee.id,
            "date_start": start,
            "date_end": end,
        }
    )


class Test(test_hr_timesheet_sheet.TestHrTimesheetSheetCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task_3 = cls.task_model.create(
            {
                "name": "Task 3",
                "project_id": cls.project_2.id,
                "company_id": cls.user.company_id.id,
            }
        )
        cls.task_4 = cls.task_model.create(
            {
                "name": "Task 4",
                "project_id": cls.project_2.id,
                "company_id": cls.user.company_id.id,
            }
        )
        cls.july = create_sheet(cls, "2030-07-01", "2030-07-07")
        cls.june = create_sheet(cls, "2030-06-17", "2030-06-23")
        vals_list = [
            sheet_vals(cls, "2030-06-18", cls.task_1, cls.june),
            sheet_vals(cls, "2030-06-20", cls.task_2, cls.june),
            sheet_vals(cls, "2030-06-22", cls.task_3, cls.june),
            sheet_vals(cls, "2030-07-03", cls.task_4, cls.july),
        ]
        cls.env["account.analytic.line"].create(vals_list)

    def test_after_setup(self):
        assert len(self.june.timesheet_ids) == 3
        assert len(self.july.timesheet_ids) == 1
        assert self.july.proposed_task_ids

    def test_remove_proposed_adding_analytic_line(self):
        assert len(self.july.proposed_task_ids) == 3
        # we only have 1 analytic.line entry for this timesheet.sheet
        assert len(self.july.timesheet_ids) == 1
        self.july.proposed_task_ids = [(6, 0, self.july.proposed_task_ids[2:].ids)]
        assert len(self.july.proposed_task_ids) == 1
        # we now have 3 analytic.line entries
        assert len(self.july.timesheet_ids) == 3

    def test_one_proposed_to_remove(self):
        self.july.proposed_task_ids = [(6, 0, self.july.proposed_task_ids[2:].ids)]
        assert len(self.july.proposed_task_ids) == 1
        self.july.proposed_task_ids = False
        assert len(self.july.proposed_task_ids) == 0
