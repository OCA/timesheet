# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrEmployeeTimesheetCostHistory(models.Model):
    _name = "hr.employee.timesheet.cost.history"
    _description = "Employee Timesheet Cost History"
    _order = "create_date DESC"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
    )
    hourly_cost = fields.Monetary(currency_field="currency_id")
    starting_date = fields.Date(
        help="The cost change has effect since this date.",
        default=fields.Date.context_today,
    )
    comment = fields.Char()
