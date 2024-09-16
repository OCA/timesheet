# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _validate_start_before_stop(self):
        for line in self:
            if line.time_stop:
                super(AccountAnalyticLine, line)._validate_start_before_stop()
        return
