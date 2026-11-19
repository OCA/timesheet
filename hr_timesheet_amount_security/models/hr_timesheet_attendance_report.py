# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class HrTimesheetAttendanceReport(models.Model):
    _inherit = "hr.timesheet.attendance.report"

    timesheets_cost = fields.Float(
        groups="analytic_amount_security.group_allow_read_analytic_amount"
    )
    attendance_cost = fields.Float(
        groups="analytic_amount_security.group_allow_read_analytic_amount"
    )
    cost_difference = fields.Float(
        groups="analytic_amount_security.group_allow_read_analytic_amount"
    )
