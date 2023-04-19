# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):

    _inherit = "account.move"

    def unlink(self):
        return super(
            AccountMove, self.with_context(timesheet_no_recompute=True)
        ).unlink()
