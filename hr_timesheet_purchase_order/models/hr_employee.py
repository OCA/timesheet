from odoo import fields, models


class HR(models.Model):
    _inherit = "hr.employee"

    recurrence_id = fields.Many2one("hr.timesheet.recurrence", copy=False)
