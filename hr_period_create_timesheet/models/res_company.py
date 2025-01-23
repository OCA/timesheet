from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    hr_period_create_months_in_advance = fields.Integer(
        string="Months to Create Periods in Advance",
        default=1,
        help="Defines how many months in advance timesheets should be created for HR periods.",
    )
