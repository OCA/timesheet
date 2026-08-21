# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    timesheet_pending_ids = fields.One2many(
        comodel_name="account.analytic.line",
        compute="_compute_timesheet_pending_ids",
        string="Pending Timesheets",
        help="Timesheets linked to this invoice's SO lines that are not yet "
        "linked to any non-cancelled invoice",
    )
    timesheet_pending_count = fields.Integer(
        string="Pending Timesheets Count",
        compute="_compute_timesheet_pending_ids",
    )
    timesheet_alert_dismissed = fields.Boolean(
        default=False,
        help="If unchecked, shows a warning alert about unlinked timesheets",
    )

    @api.depends("invoice_line_ids.sale_line_ids")
    def _compute_timesheet_pending_ids(self):
        self.timesheet_pending_ids = False
        self.timesheet_pending_count = 0
        for invoice in self.filtered_domain([("move_type", "=", "out_invoice")]):
            so_lines = invoice.invoice_line_ids.sale_line_ids
            if not so_lines:
                continue
            domain = self.env["account.move.line"]._timesheet_domain_get_invoiced_lines(
                so_lines
            )
            pending = self.env["account.analytic.line"].search(domain)
            invoice.timesheet_pending_ids = pending
            invoice.timesheet_pending_count = len(pending)

    def action_link_timesheets(self):
        self.ensure_one()
        self.timesheet_pending_ids.write({"timesheet_invoice_id": self.id})
        self.timesheet_alert_dismissed = True

    def action_dismiss_timesheet_alert(self):
        self.ensure_one()
        self.timesheet_alert_dismissed = True

    def action_select_timesheets(self):
        self.ensure_one()
        pending = self.timesheet_pending_ids
        if not pending:
            return
        return {
            "type": "ir.actions.act_window",
            "name": "Select Timesheets to Link",
            "res_model": "account.analytic.line",
            "view_mode": "list,form",
            "domain": [("id", "in", pending.ids)],
            "context": {
                "default_timesheet_invoice_id": self.id,
            },
        }

    def button_draft(self):
        res = super().button_draft()
        self.filtered(
            lambda m: m.move_type == "out_invoice"
        ).timesheet_alert_dismissed = False
        return res
