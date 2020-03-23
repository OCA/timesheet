# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related=None,
        readonly=False,
        required=True,
        default=lambda self: self._get_default_currency_id(),
        track_visibility='onchange',
    )

    def _get_default_currency_id(self):
        return self.company_id.currency_id \
            or self.env.user.company_id.currency_id
