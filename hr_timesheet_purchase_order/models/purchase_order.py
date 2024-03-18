# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _compute_timesheet_sheet_count(self):
        """
        Compute total timesheet sheets
        """
        for order in self:
            order.timesheet_sheet_count = len(order.timesheet_sheet_ids)

    timesheet_sheet_ids = fields.One2many(
        "hr_timesheet.sheet", "purchase_order_id", string="Timesheet Sheets"
    )
    timesheet_sheet_count = fields.Integer(compute="_compute_timesheet_sheet_count")

    def action_open_timesheet_sheet(self):
        """
        Open related timesheet sheets
        """
        tree_view_ref = self.env.ref(
            "hr_timesheet_sheet.hr_timesheet_sheet_tree", raise_if_not_found=False
        )
        form_view_ref = self.env.ref(
            "hr_timesheet_sheet.hr_timesheet_sheet_form", raise_if_not_found=False
        )
        action = {
            "name": "Timesheet Sheets",
            "type": "ir.actions.act_window",
            "res_model": "hr_timesheet.sheet",
            "views": [(tree_view_ref.id, "tree"), (form_view_ref.id, "form")],
            "domain": [("id", "in", self.timesheet_sheet_ids.ids)],
            "target": "current",
        }
        return action
