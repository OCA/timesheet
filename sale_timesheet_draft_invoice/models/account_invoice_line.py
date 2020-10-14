# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class AccountInvoice(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        """
        Override to link to 'timesheet_invoice_id' the invoice
        """
        invoice_line = super().create(vals)
        if (
            invoice_line.invoice_id.type == 'out_invoice'
            and invoice_line.invoice_id.state == 'draft'
        ):
            invoice_line.link_timesheets_lines()
        return invoice_line

    def link_timesheets_lines(self):
        aal_model = self.env['account.analytic.line']
        for line in self:
            if line.product_id.type == 'service':
                so_lines = line.sale_line_ids.filtered(
                    lambda sol:
                    sol.product_id.invoice_policy == 'delivery'
                    and
                    sol.product_id.service_type == 'timesheet'
                )
                domain = (
                    so_lines._timesheet_compute_delivered_quantity_domain()
                )
                domain = line._update_domain(domain)
                uninvoiced_ts_lines = (
                    aal_model.sudo().search(domain)
                )
                if uninvoiced_ts_lines:
                    uninvoiced_ts_lines.write(
                        {'timesheet_invoice_id': line.invoice_id.id}
                    )

    def _update_domain(self, domain):
        return expression.AND(
            [domain, [('timesheet_invoice_id', '=', False)]]
        )

    @api.multi
    def ail_analytic_compute_delivered_quantity(self):
        """
        Recompute qty based on analytic lines in same way as in SO
        """
        invoices = self.mapped('invoice_id')
        # The delivered quantity of Sales Lines in 'manual' mode
        # should not be erased
        self = self.filtered(
            lambda ail: ail.product_id.service_type != 'manual'
        )

        # avoid recomputation if no lines concerned
        if not self:
            return False
        product_uom = self.env['product.uom']

        for inv in invoices:
            ail_lines = self.filtered(lambda l: l.invoice_id == inv)
            so_lines = ail_lines.mapped('sale_line_ids')
            domain = [('timesheet_invoice_id', '=', inv.id)]

            data = self.env['account.analytic.line'].read_group(
                domain,
                ['so_line', 'unit_amount', 'product_uom_id'],
                ['product_uom_id', 'so_line'], lazy=False
            )

            for item in data:
                # we expect that in one invoice invoice lines have
                # unique so_line
                so_id = item['so_line'][0]
                so_line = so_lines.filtered(lambda l: l.id == so_id)
                ail = self.filtered(lambda l: l.sale_line_ids == so_line)

                # convert to uom
                uom_id = item['product_uom_id'][0]
                if not product_uom and product_uom.id != uom_id:
                    product_uom = product_uom.browse(uom_id)
                qty = item['unit_amount']
                qty = product_uom._compute_quantity(qty, ail.uom_id)
                ail.quantity = qty
        return True
