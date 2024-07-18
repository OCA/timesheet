# Copyright (C) 2024 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _timesheet_postprocess_values(self, values):
        """Override to compute the amount based on the cost rules of the time type."""
        result = super()._timesheet_postprocess_values(values)
        sudo_self = (
            self.sudo()
        )  # this creates only one env for all operation that required sudo()
        # (re)compute the amount (depending on time_type_id)
        if "time_type_id" in values:
            for timesheet in sudo_self:
                cost = timesheet._hourly_cost()
                amount = -timesheet.unit_amount * cost
                amount_converted = timesheet.employee_id.currency_id._convert(
                    amount,
                    timesheet.account_id.currency_id or timesheet.currency_id,
                    self.env.company,
                    timesheet.date,
                )
                if values["time_type_id"]:
                    amount_converted = (
                        self.env["project.time.type"]
                        .browse(values["time_type_id"])
                        ._apply_cost_rules(timesheet, amount_converted)
                    )

                result[timesheet.id].update(
                    {
                        "amount": amount_converted,
                    }
                )
        return result
