# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    timesheet_costing_id = fields.Many2one(
        comodel_name="hr.timesheet.costing",
        readonly=True,
        copy=False,
        ondelete="set null",
    )

    def action_view_timesheet_costing(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.timesheet.costing",
            "view_mode": "form",
            "res_id": self.timesheet_costing_id.id,
        }
