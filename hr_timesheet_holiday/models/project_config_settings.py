# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectConfigSettings(models.TransientModel):

    _inherit = "project.config.settings"

    timesheet_hours_per_day = fields.Float(
        string="Timesheet Hours Per Day",
        related="company_id.timesheet_hours_per_day",
        digits=(2, 2),
        default=8.0,
    )
    timesheet_holiday_use_calendar = fields.Boolean(
        string="Use Employee Working Time when creating timesheet",
        related="company_id.timesheet_holiday_use_calendar",
        help="If checked and a working time schedule is linked to the "
        "employee, use the informations provided by this schedule when "
        "creating the analytic lines for the holidays.",
    )
