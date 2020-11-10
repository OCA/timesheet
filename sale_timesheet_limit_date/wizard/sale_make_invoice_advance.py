# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    timesheet_limit_date = fields.Date(string="Timesheet Limit Date")

    @api.multi
    def create_invoices(self):
        """
        Before function invokes base method for creation of invoices.
        If timesheet_limit_date is set in wizard then set the sale.order field.
        NOTE: If multiple records selected, timesheet_limit_date is not visible
        which means it will be set to False.
        """
        if self.timesheet_limit_date:
            sale_orders = self.env["sale.order"].browse(
                self._context.get("active_ids", [])
            )
            sale_orders.timesheet_limit_date = self.timesheet_limit_date
        return super().create_invoices()
