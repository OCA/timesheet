# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    timesheet_cost_history_ids = fields.One2many(
        "hr.employee.timesheet.cost.history", "employee_id", copy=False
    )
