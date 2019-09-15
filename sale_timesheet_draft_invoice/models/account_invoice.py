# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_cancel(self):
        self._unlink_timesheet_ids()
        return super().action_invoice_cancel()

    @api.multi
    def _unlink_timesheet_ids(self):
        """
        Unlink timesheet_ids and timesheet_invoice_id on the aal
        """
        self.write({'timesheet_ids': [(5, False)]})

    @api.multi
    def action_invoice_draft(self):
        res = super().action_invoice_draft()
        self = self.with_context(not_recompute_state=True)
        if res:
            out_inv = self.filtered(lambda inv: inv.type == 'out_invoice')
            lines = out_inv.mapped('invoice_line_ids')
            lines.link_timesheets_lines()
            lines.ail_analytic_compute_delivered_quantity()
        self.compute_taxes()
        return res

    def action_invoice_paid(self):
        """
        Prevent recomputing state till all computed fields will finish
        their update, othervise invoice will be set to paid state as
        amount equal 0
        """
        if self.env.context.get('not_recompute_state'):
            return
        return super().action_invoice_paid()
