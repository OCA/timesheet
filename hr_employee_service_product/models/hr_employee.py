# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    service_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Service Product",
        domain="[('type','=','service')]",
    )


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_postprocess_values(self, values):
        result = super(AccountAnalyticLine, self)._timesheet_postprocess_values(values)
        if any(
            field_name in values
            for field_name in ["unit_amount", "employee_id", "account_id"]
        ):
            timesheet = self.browse(list(result.keys())[0])
            cost = (
                timesheet.employee_id.timesheet_cost
                or timesheet.employee_id.service_product_id.standard_price
                or 0.0
            )
            amount = -timesheet.unit_amount * cost
            amount_converted = timesheet.employee_id.currency_id._convert(
                amount,
                timesheet.account_id.currency_id,
                self.env.company,
                timesheet.date,
            )
            result[timesheet.id].update(
                {
                    "amount": amount_converted,
                    "product_id": timesheet.employee_id.service_product_id
                    and timesheet.employee_id.service_product_id.id
                    or False,
                }
            )
        return result
