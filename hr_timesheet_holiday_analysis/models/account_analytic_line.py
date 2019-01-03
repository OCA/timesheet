# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    is_leave = fields.Boolean(
        string='Is Leave',
        compute='_compute_is_leave',
        store=True,
    )

    @api.multi
    @api.depends('holiday_id')
    def _compute_is_leave(self):  # pragma: no cover
        for line in self:
            line.is_leave = bool(line.holiday_id)
