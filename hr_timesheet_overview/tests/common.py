# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from datetime import datetime

from odoo import tools
from odoo.tests.common import TransactionCase

VALID_DAYS_JAN_2022 = [
    # A tuple forming a day number and its length in days
    ((3, 1.0), (4, 1.0), (5, 0.5), (6, 1.0), (7, 1.0)),  # week 1
    ((10, 1.0), (11, 1.0), (12, 0.5), (13, 1.0), (14, 1.0)),  # week 2
    ((17, 1.0), (18, 1.0), (19, 0.5), (20, 1.0), (21, 1.0)),  # week 3
    ((24, 1.0), (25, 1.0), (26, 0.5), (27, 1.0), (28, 1.0)),  # week 4
    ((31, 1.0),),  # week 5
]

INVALID_DAYS_DEC_2021 = [
    (1, 4, 5),  # Wednesday  # Saturday  # Sunday   # week 1
    (8, 11, 12),  # Wednesday  # Saturday  # Sunday   # week 2
    (15, 18, 19),  # Wednesday  # Saturday  # Sunday   # week 3
    (22, 25, 26),  # Wednesday  # Saturday  # Sunday   # week 4
    (29,),  # Wednesday                         # week 5
]

CURRENT_CONTRACT_HEH_LINES_LENGTH = 21 + 1  # the frozen date
CURRENT_TIMESHEET_HEH_LINES_LENGTH = 21
CLOSE_CONTRACT_HEH_LINES_LENGTH = 18
TOTAL_HEH_LINES = (
    CURRENT_CONTRACT_HEH_LINES_LENGTH
    + CURRENT_TIMESHEET_HEH_LINES_LENGTH
    + CLOSE_CONTRACT_HEH_LINES_LENGTH
)


class HrDashboardCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Sofia Metaclass",
                "gender": "female",
                "country_id": cls.env.ref("base.us").id,
            }
        )
        cls.employee._compute_address_id()
        cls.full_calendar = cls._define_calendar(
            "40 Hours",
            [
                (8, 12, 0),
                (14, 17, 0),
                (8, 12, 1),
                (14, 17, 1),
                (8, 12, 2),
                (8, 12, 3),
                (14, 17, 3),
                (8, 12, 4),
                (14, 17, 4),
            ],
            "US/Eastern",
        )
        cls.reduced_calendar = cls._define_calendar(
            "35 Hours",
            [
                (8, 12, 0),
                (14, 17, 0),
                (8, 12, 1),
                (14, 17, 1),
                (8, 12, 3),
                (14, 17, 3),
                (8, 12, 4),
                (14, 17, 4),
            ],
            "US/Eastern",
        )
        cls.current_contract = cls.create_contract(
            cls.employee, cls.full_calendar, datetime(2022, 1, 1).date()
        )

        cls.close_contract = cls.create_contract(
            cls.employee,
            cls.reduced_calendar,
            datetime(2021, 12, 1).date(),
            datetime(2021, 12, 31).date(),
        )

        cls.account = cls.env["account.analytic.account"].create(
            {"name": "Analytic Account Sample"}
        )
        cls.project = cls.env["project.project"].create({"name": "Sample Project"})
        cls.task = cls.env["project.task"].create(
            {"name": "Sample Task", "project_id": cls.project.id}
        )
        all_days = []
        for week in VALID_DAYS_JAN_2022:
            all_days.extend([day for day, length in week])
        cls.timesheets = cls.create_timesheets(
            cls.account, cls.project, 2022, 1, all_days, task=cls.task
        )
        cls.timesheets_without_employee = cls.create_timesheets(
            cls.account, cls.project, 2022, 1, all_days, without_employee=True
        )

    @classmethod
    def create_timesheets(
        cls, account, project, year, month, days, task=None, without_employee=False
    ):
        with (
            tools.mute_logger(
                "odoo.addons.hr_timesheet_overview.models.hr_employee_hour"
            )
        ):
            model = cls.env["account.analytic.line"]
            records = model.create(
                [
                    {
                        "name": "Timesheet Sample",
                        "date": datetime(year, month, day).date(),
                        "employee_id": cls.employee.id
                        if not without_employee
                        else False,
                        "unit_amount": 7,
                        "account_id": account.id,
                        "project_id": project.id,
                        "task_id": task.id if task else False,
                    }
                    for day in days
                ]
            )
            records.flush()
            # Here we need to override the write and create date of each
            # timesheets to allow generation script to search them properly
            # pylint: disable=sql-injection
            query = (
                "UPDATE account_analytic_line SET create_date=date, "
                "write_date=date WHERE id in %s"
            )
            cls.env.cr.execute(query, (tuple(records.ids),))
            # pylint: enable=sql-injection
            return records

    @classmethod
    def create_contract(cls, employee, calendar, start, end=None):
        return cls.env["hr.contract"].create(
            {
                "name": calendar.name,
                "employee_id": employee.id,
                "state": "close" if end else "open",
                "kanban_state": "normal",
                "wage": 1,
                "date_start": start,
                "date_end": end,
                "resource_calendar_id": calendar.id,
            }
        )

    @classmethod
    def _define_calendar(cls, name, attendances, tz):
        return cls.env["resource.calendar"].create(
            {
                "name": name,
                "tz": tz,
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "%s_%d" % (name, index),
                            "hour_from": att[0],
                            "hour_to": att[1],
                            "dayofweek": str(att[2]),
                        },
                    )
                    for index, att in enumerate(attendances)
                ],
            }
        )

    @classmethod
    def _get_related_hours(cls, records, deleted_ids=None):
        """Use deleted_id with original id if record has been unlinked"""
        ir_model = cls.env["ir.model"].search([("model", "=", records._name)])
        return cls.env["hr.employee.hour"].search(
            [
                ("model_id", "=", ir_model.id),
                ("res_id", "in", deleted_ids or records.ids),
            ]
        )
