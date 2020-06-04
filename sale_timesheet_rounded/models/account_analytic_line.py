# Copyright 2019 Camptocamp SA
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class AccountAnalyticLine(models.Model):

    _inherit = "account.analytic.line"

    unit_amount_rounded = fields.Float(
        string="Quantity rounded",
        compute="_compute_unit_rounded",
        store=True,
        readonly=False,
        copy=False,
    )

    @api.depends("project_id", "unit_amount")
    def _compute_unit_rounded(self):
        for record in self:
            record.unit_amount_rounded = record._calc_unit_amount_rounded()

    def _calc_unit_amount_rounded(self):
        self.ensure_one()
        project_rounding = (
            self.project_id and self.project_id.timesheet_rounding_method != "NO"
        )
        if project_rounding:
            return self._calc_rounded_amount(
                self.project_id.timesheet_rounding_unit,
                self.project_id.timesheet_rounding_method,
                self.project_id.timesheet_rounding_factor,
                self.unit_amount,
            )
        else:
            return self.unit_amount

    @staticmethod
    def _calc_rounded_amount(rounding_unit, rounding_method, factor, amount):
        factor = factor / 100.0
        if rounding_unit:
            unit_amount_rounded = float_round(
                amount * factor,
                precision_rounding=rounding_unit,
                rounding_method=rounding_method,
            )
        else:
            unit_amount_rounded = amount * factor
        return unit_amount_rounded

    ####################################################
    # ORM Overrides
    ####################################################

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        """Replace the value of unit_amount by unit_amount_rounded.

        When context key `timesheet_rounding` is True
        we change the value of unit_amount with the rounded one.
        This affects `sale_order_line._compute_delivered_quantity`
        which in turns compute the delivered qty on SO line.
        """
        ctx_ts_rounded = self.env.context.get("timesheet_rounding")
        fields_local = list(fields) if fields else []
        if ctx_ts_rounded and "unit_amount_rounded" not in fields_local:
            # To add the unit_amount_rounded value on read_group
            fields_local.append("unit_amount_rounded")
        res = super().read_group(
            domain,
            fields_local,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        if ctx_ts_rounded:
            # To set the unit_amount_rounded value instead of unit_amount
            for rec in res:
                rec["unit_amount"] = rec["unit_amount_rounded"]
        return res

    def read(self, fields=None, load="_classic_read"):
        """Replace the value of unit_amount by unit_amount_rounded.

        When context key `timesheet_rounding` is True
        we change the value of unit_amount with the rounded one.
        This affects `account_analytic_line._sale_determine_order_line`.
        """
        ctx_ts_rounded = self.env.context.get("timesheet_rounding")
        fields_local = fields.copy() if fields else []
        read_unit_amount = "unit_amount" in fields_local or not fields_local
        if ctx_ts_rounded and read_unit_amount and fields_local:
            if "unit_amount_rounded" not in fields_local:
                # To add the unit_amount_rounded value on read
                fields_local.append("unit_amount_rounded")
        res = super().read(fields=fields_local, load=load)
        if ctx_ts_rounded and read_unit_amount:
            # To set the unit_amount_rounded value instead of unit_amount
            for rec in res:
                rec["unit_amount"] = rec["unit_amount_rounded"]
        return res
