# Copyright 2018-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrUtilizationAnalysis(models.TransientModel):
    _name = "hr.utilization.analysis"
    _description = "HR Utilization Analysis"

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    only_active_employees = fields.Boolean(
        string="Only Active Employees",
        default=True,
    )
    employee_ids = fields.Many2many(string="Employees", comodel_name="hr.employee")
    employee_category_ids = fields.Many2many(
        string="Employee Tags",
        comodel_name="hr.employee.category",
    )
    department_ids = fields.Many2many(
        string="Departments",
        comodel_name="hr.department",
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

            entry_ids = [(5, False, False)]
            for employee_id in employee_ids:
                date = analysis.date_from
                one_day = timedelta(days=1)
                while date <= analysis.date_to:
                    entry_ids.append(
                        (0, False, {"employee_id": employee_id.id, "date": date})
                    )
                    date += one_day

            analysis.entry_ids = entry_ids

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
        string="Employee",
        comodel_name="hr.employee",
        required=True,
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
    date = fields.Date(string="Date", required=True)
    line_ids = fields.Many2many(
        string="Timesheet Lines",
        comodel_name="account.analytic.line",
        compute="_compute_line_ids",
        store=True,
    )
    capacity = fields.Float(string="Capacity", compute="_compute_capacity", store=True)
    amount = fields.Float(string="Quantity", compute="_compute_amount", store=True)
    difference = fields.Float(
        string="Difference",
        compute="_compute_difference",
        store=True,
    )

    _sql_constraints = [
        (
            "entry_uniq",
            "UNIQUE(analysis_id, employee_id, date)",
            "An analysis entry for employee/date pair has to be unique!",
        ),
    ]

    @api.depends("employee_id", "date")
    def _compute_line_ids(self):
        AccountAnalyticLine = self.env["account.analytic.line"]

        for entry in self:
            entry.line_ids = AccountAnalyticLine.search(
                [
                    ("project_id", "!=", False),
                    ("employee_id", "=", entry.employee_id.id),
                    ("date", "=", entry.date),
                ]
            )

    @api.depends("employee_id", "date")
    def _compute_capacity(self):
        Module = self.env["ir.module.module"]

        project_timesheet_holidays = Module.sudo().search(
            [("name", "=", "project_timesheet_holidays"), ("state", "=", "installed")],
            limit=1,
        )

        for entry in self:
            tz = pytz.timezone(entry.employee_id.resource_calendar_id.tz)
            from_datetime = datetime.combine(entry.date, time.min).replace(tzinfo=tz)
            to_datetime = datetime.combine(entry.date, time.max).replace(tzinfo=tz)

            capacity = entry.employee_id._get_work_days_data(
                from_datetime,
                to_datetime,
                compute_leaves=not project_timesheet_holidays,
            )["hours"]

            if project_timesheet_holidays:
                capacity -= entry.employee_id._get_leave_days_data(
                    from_datetime,
                    to_datetime,
                    calendar=entry.employee_id.resource_calendar_id,
                )["hours"]

            entry.capacity = max(capacity, 0)

    @api.depends("line_ids")
    def _compute_amount(self):
        uom_hour = self.env.ref("uom.product_uom_hour")

        for entry in self:
            amount = 0.0
            for line_id in entry.line_ids:
                amount += line_id.product_uom_id._compute_quantity(
                    line_id.unit_amount, uom_hour
                )
            entry.amount = amount

    @api.depends("amount", "capacity")
    def _compute_difference(self):
        for entry in self:
            entry.difference = entry.capacity - entry.amount
