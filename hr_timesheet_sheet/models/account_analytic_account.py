# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    @api.constrains("company_id")
    def _check_timesheet_sheet_company_id(self):
        for rec in self.sudo():
            sheets = rec.line_ids.mapped("sheet_id").filtered(
                lambda s: s.company_id and s.company_id != rec.company_id
            )
            if sheets:
                raise ValidationError(
                    _(
                        "You cannot change the company, as this %s (%s) "
                        "is assigned to %s (%s)."
                    )
                    % (
                        rec._name,
                        rec.display_name,
                        sheets[0]._name,
                        sheets[0].display_name,
                    )
                )
