from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    timesheet_lock_weekday = fields.Selection(
        related="company_id.timesheet_lock_weekday",
        string="Weekly Cutoff Day",
        readonly=False,
    )
