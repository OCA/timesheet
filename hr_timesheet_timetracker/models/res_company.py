# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    timetracker_rounding_enabled = fields.Boolean(
        string='Apply Rounding',
    )
    timetracker_started_at_rounding = fields.Selection(
        string='Started At rounding',
        selection='_selection_rounding',
        default='DOWN',
    )
    timetracker_stopped_at_rounding = fields.Selection(
        string='Stopped At rounding',
        selection='_selection_rounding',
        default='UP',
    )

    @api.model
    def _selection_rounding(self):
        return [
            ('UP', 'To next greater'),
            ('DOWN', 'To previous lesser'),
            ('HALF-UP', 'To nearest'),
        ]
