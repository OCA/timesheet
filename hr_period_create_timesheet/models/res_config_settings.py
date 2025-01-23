from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hr_period_create_months_in_advance = fields.Integer(
        string="Months to Create Periods in Advance",
        related="company_id.hr_period_create_months_in_advance",
        readonly=False,
        help="Defines how many months in advance timesheets should be created for HR periods.",
    )
