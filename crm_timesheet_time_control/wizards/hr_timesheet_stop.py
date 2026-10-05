# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrTimesheetStop(models.TransientModel):
    _name = "hr.timesheet.stop"
    _description = "Stop Timesheet Timer Wizard"

    analytic_line_id = fields.Many2one(
        comodel_name="account.analytic.line",
        string="Timesheet Line",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Description",
        required=True,
    )

    def action_stop(self):
        self.ensure_one()
        self.analytic_line_id.write({"name": self.name})
        return self.analytic_line_id.with_context(
            skip_stop_wizard=True
        ).button_end_work()
