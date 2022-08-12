from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    allow_generate_purchase_order = fields.Boolean(
        string="Generate POs from Timesheet", default=False
    )
    billing_partner_id = fields.Many2one("res.partner")
