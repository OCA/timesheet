# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    allow_generate_purchase_order = fields.Boolean(string="Generate POs from Timesheet")
    billing_partner_id = fields.Many2one("res.partner")
