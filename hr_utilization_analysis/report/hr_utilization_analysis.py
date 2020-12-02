# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time, timedelta

import pytz

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class HrUtilizationAnalysis(models.TransientModel):
    _name = "hr.utilization.analysis"
    _description = "HR Utilization Analysis"

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    only_active_employees = fields.Boolean(
        string="Only Active Employees", default=True,
    )
    employee_ids = fields.Many2many(string="Employees", comodel_name="hr.employee")
    employee_category_ids = fields.Many2many(
        string="Employee Tags", comodel_name="hr.employee.category",
    )
    department_ids = fields.Many2many(
        string="Departments", comodel_name="hr.department",
    )
    entry_ids = fields.One2many(
        string="Entries",
        comodel_name="hr.utilization.analysis.entry",
        inverse_name="analysis_id",
        compute="_compute_entry_ids",
        store=True,
    )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for analysis in self:
            if analysis.date_from > analysis.date_to:
                raise ValidationError(_("Date-To can not be earlier than Date-From"))

    @api.depends(
        "only_active_employees",
        "employee_ids",
        "employee_category_ids",
        "department_ids",
    )
    def _compute_entry_ids(self):
        HrEmployee = self.env["hr.employee"]

        for analysis in self:
            employee_ids = HrEmployee.search(analysis._get_employees_domain())

            dates = []
            date = analysis.date_from
            one_day = timedelta(days=1)
            while date <= analysis.date_to:
                dates.append(date)
                date += one_day

            entry_ids = [(5, False, False)] + [
                (0, False, d) for d in self._get_entry_values(employee_ids, dates)
            ]

            analysis.entry_ids = entry_ids

    def _get_entry_values(self, employees, dates):
        Module = self.env["ir.module.module"]
        AccountAnalyticLine = self.env["account.analytic.line"]
        Task = self.env["project.task"]

        project_timesheet_holidays = Module.with_user(SUPERUSER_ID).search(
            [("name", "=", "project_timesheet_holidays"), ("state", "=", "installed")],
            limit=1,
        )

        uom_hour = self.env.ref("uom.product_uom_hour")

        all_line_ids = AccountAnalyticLine.search(
            [
                ("project_id", "!=", False),
                ("employee_id", "in", employees.ids),
                ("date", "in", dates),
            ]
        )
        all_tasks = Task.search(
            [
                ("user_id", "in", employees.mapped("user_id").ids),
                ("date_assign", ">=", min(dates)),
                ("date_assign", "<=", max(dates)),
            ]
        )
        entries = []
        for employee in employees:
            tz = pytz.timezone(employee.resource_calendar_id.tz)
            from_datetime = datetime.combine(min(dates), time.min).replace(tzinfo=tz)
            to_datetime = datetime.combine(max(dates), time.max).replace(tzinfo=tz)
            work_time = employee.list_work_time_per_day(from_datetime, to_datetime)
            hours_dict = {w[0]: w[1] for w in work_time}
            if project_timesheet_holidays:
                leaves = employee.list_leaves(from_datetime, to_datetime)
                leaves_dict = {e[0]: e[1] for e in leaves}

            for date in dates:
                line_ids = all_line_ids.filtered(
                    lambda l: l.employee_id == employee and l.date == date
                )
                base_entry = {"employee_id": employee.id, "date": date}

                capacity = hours_dict.get(date, 0)
                if project_timesheet_holidays:
                    capacity -= leaves_dict.get(date, 0)
                capacity = max(capacity, 0)

                tasks = all_tasks.filtered(
                    lambda t: t.user_id == employee.user_id
                    and t.date_assign.date() == date
                )
                planned_hours = sum(tasks.mapped("planned_hours"))

                projects = line_ids.mapped("project_id")
                if not projects:
                    entry = base_entry.copy()
                    entry["amount"] = 0.0
                    entry["line_ids"] = [(4, _id) for _id in line_ids.ids]
                    entry["capacity"] = entry["difference"] = capacity
                    entry["planned_amount"] = planned_hours
                    entry["planned_difference"] = capacity - planned_hours
                    entries.append(entry)
                    continue

                capacity = capacity / len(projects)  # TODO: improve
                for project in projects:
                    amount = 0.0
                    project_line_ids = line_ids.filtered(
                        lambda l: l.project_id == project
                    )
                    entry = base_entry.copy()
                    entry["line_ids"] = [(4, _id) for _id in project_line_ids.ids]
                    for line_id in project_line_ids:
                        amount += line_id.product_uom_id._compute_quantity(
                            line_id.unit_amount, uom_hour
                        )
                    project_tasks = tasks.filtered(lambda t: t.project_id == project)
                    planned_hours = sum(project_tasks.mapped("planned_hours"))
                    entry["amount"] = amount
                    entry["capacity"] = capacity
                    entry["difference"] = capacity - amount
                    entry["project_id"] = project.id
                    entry["planned_amount"] = planned_hours
                    entry["planned_difference"] = planned_hours - capacity
                    entries.append(entry)

        return entries

    def _get_employees_domain(self):
        self.ensure_one()

        query = []

        if self.only_active_employees:
            query.append(("active", "=", True))
        employee_ids = self.employee_ids | self.employee_category_ids.mapped(
            "employee_ids"
        )
        if employee_ids:
            query.append(("id", "in", employee_ids.ids))
        if self.department_ids:
            query.append(("department_id", "in", self.department_ids.ids))

        return query


class HrUtilizationAnalysisEntry(models.TransientModel):
    _name = "hr.utilization.analysis.entry"
    _description = "HR Utilization Analysis entry"

    analysis_id = fields.Many2one(
        string="Analysis",
        comodel_name="hr.utilization.analysis",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(related="employee_id.name", store=True)
    employee_id = fields.Many2one(
        string="Employee", comodel_name="hr.employee", required=True,
    )
    department_id = fields.Many2one(
        string="Department",
        comodel_name="hr.department",
        related="employee_id.department_id",
        store=True,
    )
    manager_id = fields.Many2one(
        string="Manager",
        comodel_name="hr.employee",
        related="employee_id.parent_id",
        store=True,
    )
    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    date = fields.Date(required=True)
    line_ids = fields.Many2many(
        string="Timesheet Lines", comodel_name="account.analytic.line",
    )

    capacity = fields.Float()
    amount = fields.Float(string="Real")
    difference = fields.Float(string="Capacity remaining")
    planned_amount = fields.Float(string="Planned")
    planned_difference = fields.Float(string="Still to plan")

    _sql_constraints = [
        (
            "entry_uniq",
            "UNIQUE(analysis_id, project_id, employee_id, date)",
            "An analysis entry for employee/date/project combination has to be unique!",
        ),
    ]
