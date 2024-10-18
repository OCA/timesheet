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
                lambda s, rec=rec: s.company_id and s.company_id != rec.company_id
            )
            if sheets:
                raise ValidationError(
                    _(
                        "You cannot change the company, as this "
                        "%(rec_name)s (%(rec_display_name)s) is assigned "
                        "to %(current_name)s (%(current_display_name)s).",
                        rec_name=rec._name,
                        rec_display_name=rec.display_name,
                        current_name=sheets[0]._name,
                        current_display_name=sheets[0].display_name,
                    )
                )
