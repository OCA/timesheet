# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    timetracker_rounding_enabled = fields.Boolean(
        related='company_id.timetracker_rounding_enabled',
        readonly=False,
    )
    timetracker_started_at_rounding = fields.Selection(
        related='company_id.timetracker_started_at_rounding',
        readonly=False,
    )
    timetracker_stopped_at_rounding = fields.Selection(
        related='company_id.timetracker_stopped_at_rounding',
        readonly=False,
    )
