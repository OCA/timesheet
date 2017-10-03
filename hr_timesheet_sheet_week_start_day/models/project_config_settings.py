# -*- coding: utf-8 -*-
# Copyright 2015-17 Eficent Business and IT Consulting Services S.L.
#     (www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectConfigSettings(models.TransientModel):
    _inherit = 'project.config.settings'

    timesheet_week_start = fields.Selection(
        related='company_id.timesheet_week_start', string="Week start day")
