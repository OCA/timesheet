# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrPeriodCreateTimesheet(models.TransientModel):
    _name = "hr.period.create.timesheet"
    _description = "Hr Period Create Timesheet"

    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="hr_employee_hr_period_create_timesheet_rel",
        column1="wiz_id",
        column2="employee_id",
        string="Employees",
    )

    @api.model
    def default_get(self, fields):
        res = super(HrPeriodCreateTimesheet, self).default_get(fields)
        period_obj = self.env["hr.period"]
        period_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model")

        if not period_ids:
            return res
        assert active_model == "hr.period", "Bad context propagation"

        company_id = False
        for period in period_obj.browse(period_ids):
            if company_id and company_id != period.company_id.id:
                raise ValidationError(_("All periods must belong to the same company."))
            company_id = period.company_id.id
        res["employee_ids"] = []
        return res

    @api.model
    def _prepare_timesheet(self, employee, hr_period):
        return {
            "employee_id": employee.id,
            "date_start": hr_period.date_start,
            "date_end": hr_period.date_end,
            "company_id": hr_period.company_id.id,
            "department_id": employee.department_id.id,
            "hr_period_id": hr_period.id,
        }

    def compute(self):
        res = []
        hr_period_obj = self.env["hr.period"]
        timesheet_obj = self.env["hr_timesheet.sheet"]
        for wiz_data in self:
            hr_period_ids = self.env.context.get("active_ids", [])
            periods = hr_period_obj.browse(hr_period_ids)
            for employee in wiz_data.employee_ids:
                for hr_period in periods:
                    timesheet_ids = timesheet_obj.search(
                        [
                            ("employee_id", "=", employee.id),
                            ("date_start", "<=", hr_period.date_end),
                            ("date_end", ">=", hr_period.date_start),
                        ]
                    )
                    if timesheet_ids:
                        raise ValidationError(
                            _(
                                "Employee %(emp_name)s already has a Timesheet within the "
                                "date range of HR Period %(period_name)s."
                            )
                            % (
                                {
                                    "emp_name": employee.name,
                                    "period_name": hr_period.name,
                                }
                            )
                        )
                    ts_data = self._prepare_timesheet(employee, hr_period)
                    ts_id = timesheet_obj.create(ts_data)
                    res.append(ts_id.id)

        return {
            "domain": "[('id','in', [" + ",".join(map(str, res)) + "])]",
            "name": _("Employee Timesheets"),
            "view_mode": "tree,form",
            "res_model": "hr_timesheet.sheet",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }

    def create_timesheets_on_future_periods(self):
        timesheet_obj = self.env["hr_timesheet.sheet"]
        today = fields.Date.today()
        periods = self.env["hr.period"].search([("date_end", ">=", today)])
        employees = self.env["hr.employee"].search([("user_id", "!=", False)])
        if not periods or not employees:
            return
        # Create a dictionary to store existing timesheets per employee
        existing_timesheets = {}
        timesheet_domain = [
            ("employee_id", "in", employees.ids),
            ("date_start", "<=", max(periods.mapped("date_end"))),
            ("date_end", ">=", min(periods.mapped("date_start"))),
        ]
        for timesheet in timesheet_obj.search(timesheet_domain):
            key = (timesheet.employee_id.id, timesheet.date_start, timesheet.date_end)
            existing_timesheets[key] = timesheet

        for hr_period in periods:
            for employee in employees:
                key = (employee.id, hr_period.date_start, hr_period.date_end)
                if key not in existing_timesheets:
                    ts_data = self._prepare_timesheet(employee, hr_period)
                    timesheet_obj.create(ts_data)
