# Copyright 2018-2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    exclude_from_sale_order = fields.Boolean(
        string="Non-billable",
        help="Checking this would exclude this timesheet entry from Sale Order",
        groups="sale_timesheet_line_exclude.group_exclude_from_sale_order",
    )

    @api.constrains("exclude_from_sale_order")
    def _constrains_exclude_from_sale_order(self):
        for line in self:
            if (
                line.timesheet_invoice_id
                and line.so_line.product_id.invoice_policy == "delivery"
            ):
                raise ValidationError(
                    _(
                        "You can not modify timesheets in a way that would affect "
                        "invoices since these timesheets were already invoiced."
                    )
                )

    @api.depends("exclude_from_sale_order")
    def _compute_timesheet_invoice_type(self):
        res = super()._compute_timesheet_invoice_type()
        for line in self:
            if line.exclude_from_sale_order:
                line.timesheet_invoice_type = "non_billable"
        return res

    @api.depends("exclude_from_sale_order")
    def _compute_so_line_on_exclude(self):
        self._compute_so_line()

    def _timesheet_determine_sale_line(self):
        self.ensure_one()
        if self.exclude_from_sale_order:
            return False
        return super()._timesheet_determine_sale_line()

    def _timesheet_postprocess(self, values):
        if "exclude_from_sale_order" in values:
            self._compute_so_line()
        return super()._timesheet_postprocess(values)
