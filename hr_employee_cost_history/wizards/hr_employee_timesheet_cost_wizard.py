# Copyright 2022-2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class HrEmployeeTimesheetCost(models.TransientModel):
    _name = "hr.employee.timesheet.cost.wizard"
    _description = "Employee timesheet cost wizard"

    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", ondelete="cascade", required=True
    )
    currency_id = fields.Many2one(
        "res.currency", string="Currency", ondelete="cascade", required=True
    )
    hourly_cost = fields.Monetary(currency_field="currency_id", required=True)
    starting_date = fields.Date(
        required=True,
        help="Change timesheet cost from this date onwards.",
        default=fields.Datetime.now,
        string="From Date",
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        rec.update(
            {
                "currency_id": self.env.company.currency_id.id,
            }
        )
        return rec

    def update_employee_cost(self):
        """Recalculates employee timesheet cost from the given date.

        This method uses the base function _timesheet_postprocess from
        account_analytic_line (hr_timesheet) to recalculate employee costs.
        Finally logs cost changes in cost history model.
        """
        self.ensure_one()
        bad_costs = self.employee_id.timesheet_cost_history_ids.filtered_domain(
            [("starting_date", ">=", self.starting_date)]
        )
        costs = self.employee_id.timesheet_cost_history_ids - bad_costs
        self.employee_id.sudo().write(
            {
                "hourly_cost": self.hourly_cost,
                "timesheet_cost_history_ids": [
                    fields.Command.set(costs.ids),
                    fields.Command.create(
                        {
                            "employee_id": self.employee_id.id,
                            "currency_id": self.currency_id.id,
                            "hourly_cost": self.hourly_cost,
                            "starting_date": self.starting_date,
                        }
                    ),
                ],
            }
        )
        timesheet_ids = self.env["account.analytic.line"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("date", ">=", self.starting_date),
            ]
        )
        timesheet_ids._timesheet_postprocess({"employee_id": self.employee_id.id})
